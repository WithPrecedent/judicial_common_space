"""Finds the NOMINATE scores of senators and presidents, and of justices.

The Judicial Common Space puts judges, justices, members of Congress, and
presidents on the scale of the first dimension of NOMINATE, on which higher
scores are more conservative. Voteview's DW-NOMINATE scores ("nominate_dim1"
in its file of members, which courtpy uses too) are on one scale for both
chambers and the president, and each member has one score for the whole of
the member's service. They are the scores that the current Judicial Common
Space files use.

A `Senate` finds the senators from a state who belonged to a president's
party when a judge was appointed, in one of two ways:

* `"congress"`: every senator from the state who sat in the Congress of the
  appointment and belonged to the party (by Voteview's record of that
  Congress). This is how the published Judicial Common Space scores were
  made: in a Congress in which a senator died or resigned, the judge can get
  the mean of three senators.
* `"date"`: the senators who held the state's seats on the day of the
  appointment and belonged to the party on that day (by the dates of
  service in https://github.com/unitedstates/congress-legislators). This is
  the rule as Epstein et al. state it (the "home-state Senators" of "the
  delegation"), and is closest to how Christina Boyd made her scores of
  district judges.

`justices` puts the justices' Martin-Quinn scores on the same scale with
Epstein et al.'s arctangent transformation (their equation 2).

Contents:
    Senate: finds the scores of senators and presidents.
    congress: returns the number of the Congress that sat on a day.
    justices: returns each justice's Judicial Common Space score in each
        term.
    _LEGISLATIVE_PARTIES: the parties of presidents, by the names that the
        file of senators' dates gives them.

"""

from __future__ import annotations

import dataclasses
import json
import math
import pathlib
from collections.abc import Iterable
from typing import Any

import pandas as pd

from . import options, utilities

_LEGISLATIVE_PARTIES: dict[str, str] = {
    'Democrat': 'Democratic', 'Republican': 'Republican'}


@dataclasses.dataclass
class Senate:
    """Finds the scores of senators and presidents.

    Attributes:
        members: Voteview's table of the members of every Congress, with the
            columns "congress", "chamber", "icpsr", "state_abbrev",
            "party_code", "bioname", "bioguide_id", and "nominate_dim1".
        terms: the dates that senators served, with a row for each span of a
            term in which a senator belonged to one party: "bioguide",
            "state", "start", "end" (as YYYY-MM-DD, the day the senator left
            or the term ended), and "party". Only needed by `senators` with
            `how = "date"`.

    """

    members: pd.DataFrame
    terms: pd.DataFrame = dataclasses.field(
        default_factory = lambda: pd.DataFrame(
            columns = ['bioguide', 'state', 'start', 'end', 'party']))

    def __post_init__(self) -> None:
        """Keeps the senators and the presidents apart."""
        members = self.members
        self._senators = members[members['chamber'] == 'Senate']
        presidents = members[members['chamber'] == 'President']
        presidents = presidents.drop_duplicates('icpsr')
        self._presidents = dict(zip(
            presidents['icpsr'].astype(int),
            pd.to_numeric(presidents['nominate_dim1'], errors = 'coerce'),
            strict = True))

    @classmethod
    def from_files(
        cls,
        congress: pd.DataFrame | pathlib.Path | str,
        legislators: Iterable[pathlib.Path | str] = ()) -> Senate:
        """Makes a `Senate` from Voteview's file and the files of dates.

        Args:
            congress: Voteview's file of members ("HSall_members.csv"), as a
                path or a table.
            legislators: the files of congress-legislators with senators'
                terms ("legislators-historical.json" and
                "legislators-current.json"). Defaults to none, which is
                enough for `how = "congress"`.

        Returns:
            The `Senate`.

        """
        members = (
            congress.copy() if isinstance(congress, pd.DataFrame)
            else utilities.read_csv(congress))
        rows = []
        for path in legislators:
            with pathlib.Path(path).open(encoding = 'utf-8') as file:
                people = json.load(file)
            for person in people:
                rows.extend(_spans(person))
        terms = pd.DataFrame(
            rows, columns = ['bioguide', 'state', 'start', 'end', 'party'])
        return cls(members = members, terms = terms)

    def president(self, name: str) -> float | None:
        """Returns a president's score.

        Args:
            name: the president's name, as the Federal Judicial Center gives
                it (such as "William J. Clinton").

        Returns:
            The president's score, or `None` if Voteview has none (as for
                Herbert Hoover) or the president is unknown.

        """
        icpsr = options._PRESIDENTS.get(name)
        score = self._presidents.get(icpsr) if icpsr else None
        return None if score is None or math.isnan(score) else float(score)

    def senators(
        self,
        state: str,
        date: str,
        party: str,
        how: str = 'congress') -> list[tuple[str, float]]:
        """Returns the senators of a state who belonged to a party.

        Args:
            state: the state's postal code.
            date: the day of the appointment, as YYYY-MM-DD.
            party: the president's party, "Democratic" or "Republican".
            how: "congress" for every senator who sat in the Congress of
                `date`, or "date" for the senators who served on `date`
                (see the module's documentation). Defaults to "congress".

        Raises:
            ValueError: if `how` is neither "congress" nor "date".

        Returns:
            The name and score of each senator, in Voteview's order. A
                senator without a score (who served too briefly to vote) is
                left out.

        """
        code = options._PARTY_CODES.get(party)
        if code is None or not date:
            return []
        number = congress(date)
        senate = self._senators
        rows = senate[
            (senate['congress'] == number) & (senate['state_abbrev'] == state)]
        if how == 'congress':
            rows = rows[rows['party_code'] == code]
        elif how == 'date':
            terms = self.terms
            serving = terms[
                (terms['state'] == state) & (terms['start'] <= date)
                & (terms['end'] > date) & (terms['party'] == party)]
            rows = rows[rows['bioguide_id'].isin(set(serving['bioguide']))]
            # A senator who changed parties has a row (and a score) for each
            # party in that Congress, so the row of the party is used.
            same = rows['party_code'] == code
            switched = rows['bioguide_id'].isin(
                set(rows.loc[same, 'bioguide_id']))
            rows = rows[same | ~switched]
        else:
            message = f'how must be "congress" or "date", not {how!r}'
            raise ValueError(message)
        rows = rows.drop_duplicates('icpsr')
        scores = pd.to_numeric(rows['nominate_dim1'], errors = 'coerce')
        return [
            (str(name), float(score))
            for name, score in zip(rows['bioname'], scores, strict = True)
            if not math.isnan(score)]


def congress(date: str) -> int:
    """Returns the number of the Congress that sat on a day.

    Since 1935, each Congress has begun on January 3 of an odd year; before,
    on March 4. The first Congress began in 1789.

    Args:
        date: the day, as YYYY-MM-DD.

    Returns:
        The number of the Congress.

    """
    year = int(date[:4])
    start = '01-03' if year >= 1935 else '03-04'
    if year % 2 == 1 and date[5:10] < start:
        year -= 1
    return (year - 1789) // 2 + 1


def justices(
    source: pd.DataFrame | pathlib.Path | str,
    transformation: str | tuple[float, float] = 'jcs2024') -> pd.DataFrame:
    """Returns each justice's Judicial Common Space score in each term.

    The score is `2 / pi * arctan(b0 + b1 * MQ)`, where MQ is the justice's
    Martin-Quinn score in the term (the mean of its estimates, "post_mn").
    Epstein et al. estimated b0 and b1 (-0.1736 and 0.461) from the
    Martin-Quinn and Common Space scores of 2005, which have both been
    rescaled since. The 2024 release of the scores used new estimates (0.1934
    and 0.6025), which put today's Martin-Quinn scores where the published
    scores are.

    Args:
        source: the "justices" file of Martin-Quinn scores, as a path or a
            table, with the columns "term", "justice", "justiceName", and
            "post_mn".
        transformation: "jcs2024" or "paper" (see `options._ARCTANGENT`), or
            the intercept and slope. Defaults to "jcs2024".

    Raises:
        KeyError: if `source` lacks a column that is needed.
        ValueError: if `transformation` is an unknown name.

    Returns:
        A table with "term" (the year in which the term began, in October),
            "justice" and "justiceName" (the Supreme Court Database's number
            and name for the justice, such as 117 and "ACBarrett"),
            "martin_quinn", and "jcs".

    """
    scores = (
        source.copy() if isinstance(source, pd.DataFrame)
        else utilities.read_csv(source))
    needed = ['term', 'justice', 'justiceName', 'post_mn']
    missing = [column for column in needed if column not in scores.columns]
    if missing:
        message = (
            f'the file of Martin-Quinn scores needs the columns {missing}, '
            f'which are missing')
        raise KeyError(message)
    if isinstance(transformation, str):
        if transformation not in options._ARCTANGENT:
            message = (
                f'transformation must be among {list(options._ARCTANGENT)}, '
                f'not {transformation!r}')
            raise ValueError(message)
        transformation = options._ARCTANGENT[transformation]
    intercept, slope = transformation
    mq = pd.to_numeric(scores['post_mn'], errors = 'coerce')
    return pd.DataFrame({
        'term': pd.to_numeric(scores['term'], errors = 'coerce').astype(
            'Int64'),
        'justice': scores['justice'],
        'justiceName': scores['justiceName'],
        'martin_quinn': mq,
        'jcs': [2 / math.pi * math.atan(intercept + slope * value)
                for value in mq]})


""" Private Functions """


def _spans(person: dict[str, Any]) -> list[tuple[str, str, str, str, str]]:
    """Returns the spans of a person's Senate terms in each party.

    Args:
        person: a person in a file of congress-legislators.

    Returns:
        The person's bioguide number, state, first and last days, and party
            (as "Democratic" or "Republican", or the file's name of another
            party) for each span.

    """
    bioguide = person.get('id', {}).get('bioguide', '')
    spans = []
    for term in person.get('terms', []):
        if term.get('type') != 'sen':
            continue
        affiliations = term.get('party_affiliations') or [
            {'start': term['start'], 'end': term['end'],
             'party': term.get('party', '')}]
        for affiliation in affiliations:
            party = affiliation.get('party', '')
            spans.append((
                bioguide, term['state'], affiliation['start'],
                affiliation['end'], _LEGISLATIVE_PARTIES.get(party, party)))
    return spans
