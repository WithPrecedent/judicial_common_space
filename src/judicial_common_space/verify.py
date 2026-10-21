"""Compares the scores with published scores.

| Check | Published scores | Matched by |
| --- | --- | --- |
| `circuit_judges` | The Judicial Common Space scores of the judges of the courts of appeals (Epstein et al.'s "coa_judges" file, from https://epstein.wustl.edu/jcs). | The judge's name and circuit (see `match_name`). |
| `district_judges` | Christina Boyd's scores of district judges, made by the same rule from the Federal Judicial Center's list of judges and Voteview's scores. | The center's "nid". |
| `justices` | The Judicial Common Space scores of the justices in each term (the "supreme_court_long" file). | The term and the Supreme Court Database's name for the justice. |

`use_published` can put the published score in place of a computed one
that differs from it by more than 0.05 (`--use-published`).

Each comparison is "same" if the scores differ by less than 0.0005 (the
rounding of NOMINATE scores to three places), "close" if they differ by less
than 0.02, and "different" otherwise. Voteview estimates the scores of every
member who is serving again whenever it adds a Congress, so the scores of a
judge whose senators or president are still in office drift a little from
those that were published with an older file: such differences are "close".

Contents:
    circuit_judges: compares the scores of judges of the courts of appeals.
    district_judges: compares the scores of district judges.
    justices: compares the scores of justices in each term.
    mark_computed: adds the columns that say where each score came from.
    match_name: returns the "nid" of a judge in the Judicial Common Space
        file of judges.
    summarize: returns the agreement of each comparison.
    use_published: uses the published scores that differ from the computed
        ones.

"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from typing import Any

import pandas as pd

_CLOSE: float = 0.02
_CORRECTIONS: dict[tuple[str, int], tuple[str, int]] = {
    ('Evans, Terrance', 7): ('Evans, Terence', 7),
    ('Hunsaker, Danielle', 9): ('Forrest, Danielle', 9),
    ('Kastas, Gregory', 12): ('Katsas, Gregory', 12),
    ('McKeauge, David', 6): ('McKeague, David', 6),
    ('Moore, John P.', 10): ('Porfilio, John', 10),
    ('Owen, Priscilla', 5): ('Richman, Priscilla', 5),
    ('Shepard, Bobby', 8): ('Shepherd, Bobby', 8),
    ('Stark, Leonard', 12): ('Stark, Leonard', 13),
    ('Torruella del Valle, Juan R.', 1): ('Torruella, Juan R.', 1),
    ('Van Osterhout, Martin D.', 8): ('Van Oosterhout, Martin D.', 8)}
_PUBLISHED_THRESHOLD: float = 0.05
_SAME: float = 0.0005
_SUFFIXES: frozenset[str] = frozenset({'jr', 'sr', 'i', 'ii', 'iii', 'iv'})
_DETAILS: tuple[str, ...] = (
    'home_state', 'state_source', 'duty_station', 'method', 'senators',
    'president', 'appointment_date')


def circuit_judges(
    scored: pd.DataFrame,
    published: pd.DataFrame) -> pd.DataFrame:
    """Compares the scores of judges of the courts of appeals.

    Args:
        scored: the scores of the appointments (see
            `scores.appointments`), with the judges' names.
        published: the published scores, with the columns "name",
            "circuit", and "jcs".

    Returns:
        A row for each judge of the published file, with "name", "circuit",
            "nid", "published", "computed", "difference", "agreement", and
            how the computed score was found.

    """
    appeals = scored[scored['court_type'] == 'U.S. Court of Appeals']
    rows = []
    for record in published.to_dict('records'):
        name, circuit = str(record['name']), int(record['circuit'])
        name, circuit = _CORRECTIONS.get((name, circuit), (name, circuit))
        court = appeals[appeals['circuit'] == circuit]
        nid = match_name(name, court)
        mine = court[court['nid'] == nid].head(1)
        rows.append({
            'name': record['name'], 'circuit': circuit, 'nid': nid,
            **_compare(record['jcs'], mine)})
    return _finish(pd.DataFrame(rows))


def district_judges(
    scored: pd.DataFrame,
    published: pd.DataFrame) -> pd.DataFrame:
    """Compares the scores of district judges.

    A judge who was appointed to more than one district court has one score
    in the published file, which is compared with that of the judge's first
    appointment to a district court.

    Args:
        scored: the scores of the appointments (see `scores.appointments`).
        published: Boyd's scores, with the columns "nid", "judgename", and
            "ideology_score".

    Returns:
        A row for each judge of the published file, with "name", "nid",
            "published", "computed", "difference", "agreement", and how the
            computed score was found.

    """
    district = scored[
        (scored['court_type'] == 'U.S. District Court')
        & ~scored['reassigned'].astype(bool)]
    district = district.sort_values(['nid', 'sequence'])
    rows = []
    for record in published.to_dict('records'):
        nid = pd.to_numeric(record['nid'], errors = 'coerce')
        nid = None if pd.isna(nid) else int(nid)
        mine = district[district['nid'] == nid].head(1)
        rows.append({
            'name': record['judgename'], 'nid': nid,
            'court': mine['court'].iloc[0] if len(mine) else None,
            **_compare(record['ideology_score'], mine)})
    return _finish(pd.DataFrame(rows))


def justices(
    terms: pd.DataFrame,
    published: pd.DataFrame) -> pd.DataFrame:
    """Compares the scores of justices in each term.

    Args:
        terms: the justices' scores (see `scores.justices`).
        published: the published scores, with the columns "term",
            "justiceName", and "jcs".

    Returns:
        A row for each justice and term of the published file, with "term",
            "justiceName", "judge", "nid", "published", "computed",
            "difference", and "agreement".

    """
    mine = terms[['term', 'justiceName', 'judge', 'nid', 'jcs']].rename(
        columns = {'jcs': 'computed'})
    theirs = published[['term', 'justiceName', 'jcs']].rename(
        columns = {'jcs': 'published'})
    theirs = theirs.assign(term = pd.to_numeric(theirs['term']).astype(int))
    merged = theirs.merge(mine, on = ['term', 'justiceName'], how = 'left')
    merged['difference'] = merged['computed'] - merged['published']
    return _finish(merged)


def match_name(name: str, court: pd.DataFrame) -> int | None:
    """Returns the "nid" of a judge in the Judicial Common Space file of judges.

    The file names a judge as "Last, First Middle" (with any suffix, such as
    "Jr.", after another comma). The judge is the one judge of `court`
    whose last name is the file's (or contains its words, as "Barrett, Amy
    Coney" contains "Coney Barrett"), told apart from others with the same
    last name by the first name or initial, and then by the suffix.

    Args:
        name: the judge's name in the file.
        court: the appointments to the judge's court (see
            `scores.appointments`), with the judges' names.

    Returns:
        The judge's "nid", or `None` if no judge or more than one fits.

    """
    last, _, rest = name.partition(',')
    surname = _words(last)
    given = [word for word in _words(rest) if word not in _SUFFIXES]
    suffixes = [word for word in _words(rest) if word in _SUFFIXES]
    people = court.drop_duplicates('nid')
    fits = []
    for person in people.to_dict('records'):
        theirs = _words(str(person['judge']).partition(',')[0])
        everything = set(_words(str(person['judge'])))
        if surname == theirs or (
            len(surname) > 1 and set(surname) <= everything) or (
            ''.join(surname) == ''.join(theirs)):
            fits.append(person)
    if len(fits) > 1 and given:
        first = given[0]
        # A first name may be an initial or short for the center's ("Sam"
        # for "Samuel").
        named = [
            person for person in fits
            if any(
                word == first or (len(first) == 1 and word[0] == first)
                or (len(first) > 2 and word.startswith(first))
                for word in _words(str(person['judge']).partition(',')[2]))]
        fits = named or fits
    if len(fits) > 1 and suffixes:
        fits = [
            person for person in fits
            if suffixes[0] in _words(str(person['judge']).partition(',')[2])]
    return int(fits[0]['nid']) if len(fits) == 1 else None


def mark_computed(table: pd.DataFrame) -> pd.DataFrame:
    """Adds the columns that say where each score came from.

    Args:
        table: scores of appointments (see `scores.appointments`) or of
            justices' terms (see `scores.justices`), with a "jcs" column.

    Returns:
        A copy of the table with "computed_jcs" (the computed score) before
            "jcs" and "jcs_source" ("computed") after it, unless it has them.

    """
    table = table.copy()
    if 'jcs' not in table.columns or 'jcs_source' in table.columns:
        return table
    table.insert(list(table.columns).index('jcs'), 'computed_jcs', table['jcs'])
    table.insert(list(table.columns).index('jcs') + 1, 'jcs_source', 'computed')
    return table


def use_published(
    scored: pd.DataFrame,
    terms: pd.DataFrame,
    checks: Mapping[str, pd.DataFrame],
    threshold: float = _PUBLISHED_THRESHOLD) -> tuple[
        pd.DataFrame, pd.DataFrame]:
    """Uses the published scores that differ from the computed ones.

    Where a published score and the computed one differ by more than
    `threshold`, the appointment (or the justice's term) gets the published
    score, and "jcs_source" names where it came from: "Epstein et al." for
    the Judicial Common Space scores of circuit judges and justices, and
    "Boyd" for district judges. The appointment that gets it is the one that
    the check compared (see `circuit_judges` and `district_judges`). A
    justice's appointment gets the published score of its first term if that
    term's score was replaced.

    Args:
        scored: the scores of the appointments (see `scores.appointments`).
        terms: the justices' scores (see `scores.justices`).
        checks: the results of `circuit_judges`, `district_judges`, and
            `justices`, by the name of each check. Checks that are missing
            change nothing.
        threshold: the largest difference that keeps the computed score.
            Defaults to 0.05.

    Returns:
        The two tables, with "computed_jcs" and "jcs_source" (see
            `mark_computed`).

    """
    scored = mark_computed(scored)
    terms = mark_computed(terms)

    def large(name: str) -> pd.DataFrame:
        check = checks.get(name)
        if check is None or check.empty:
            return pd.DataFrame()
        difference = pd.to_numeric(check['difference'], errors = 'coerce')
        return check[difference.abs() > threshold]

    for row in large('circuit_judges').to_dict('records'):
        rows = scored.index[
            (scored['court_type'] == 'U.S. Court of Appeals')
            & (scored['nid'] == row['nid'])
            & (scored['circuit'] == row['circuit'])][:1]
        _replace(scored, rows, row['published'], 'Epstein et al.')
    for row in large('district_judges').to_dict('records'):
        district = scored[
            (scored['court_type'] == 'U.S. District Court')
            & ~scored['reassigned'].astype(bool)
            & (scored['nid'] == row['nid'])]
        rows = district.sort_values('sequence').index[:1]
        _replace(scored, rows, row['published'], 'Boyd')
    for row in large('justices').to_dict('records'):
        rows = terms.index[
            (terms['term'] == row['term'])
            & (terms['justiceName'] == row['justiceName'])]
        _replace(terms, rows, row['published'], 'Epstein et al.')
    if not terms.empty and 'jcs_source' in terms.columns:
        known = terms.dropna(subset = ['nid', 'sequence']).sort_values('term')
        first = known.drop_duplicates(['nid', 'sequence'])
        first = first[first['jcs_source'] != 'computed']
        for row in first.to_dict('records'):
            rows = scored.index[
                (scored['court_type'] == 'Supreme Court')
                & (scored['nid'] == row['nid'])
                & (scored['sequence'] == row['sequence'])]
            _replace(scored, rows, row['jcs'], row['jcs_source'])
    return scored, terms


def summarize(checks: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Returns the agreement of each comparison.

    Args:
        checks: the results of `circuit_judges`, `district_judges`, and
            `justices`, by the name of each check.

    Returns:
        A row for each check, with the number of published scores, the
            number that were found, and the number and share of those that
            are the same, close, and different, the correlation of the
            scores (missing if either set does not vary), and the mean
            absolute difference.

    """
    rows = []
    for name, check in checks.items():
        found = check[check['agreement'] != 'not found']
        counts = found['agreement'].value_counts()
        total = max(len(found), 1)
        published = found['published'].astype(float)
        computed = found['computed'].astype(float)
        varied = len(found) > 1 and published.std() > 0 and computed.std() > 0
        rows.append({
            'check': name,
            'published': len(check),
            'found': len(found),
            'same': int(counts.get('same', 0)),
            'close': int(counts.get('close', 0)),
            'different': int(counts.get('different', 0)),
            'share_same': counts.get('same', 0) / total,
            'share_same_or_close': (
                counts.get('same', 0) + counts.get('close', 0)) / total,
            'correlation': published.corr(computed) if varied else None,
            'mean_absolute_difference': (
                found['difference'].astype(float).abs().mean()
                if len(found) else None)})
    return pd.DataFrame(rows)


""" Private Functions """


def _compare(published: Any, mine: pd.DataFrame) -> dict[str, object]:
    """Returns the published and computed scores of a judge, and the details.

    Args:
        published: the published score.
        mine: the judge's row of the computed scores, or no rows.

    Returns:
        "published", "computed", "difference", and the columns of
            `_DETAILS`.

    """
    computed = mine['jcs'].iloc[0] if len(mine) else None
    computed = None if computed is None or pd.isna(computed) else float(
        computed)
    value = pd.to_numeric(published, errors = 'coerce')
    value = None if pd.isna(value) else float(value)
    return {
        'published': value,
        'computed': computed,
        'difference': (
            None if computed is None or value is None else computed - value),
        **{column: (mine[column].iloc[0] if len(mine) else None)
           for column in _DETAILS}}


def _finish(table: pd.DataFrame) -> pd.DataFrame:
    """Adds the agreement of each comparison.

    Args:
        table: a table with "published", "computed", and "difference".

    Returns:
        The table, with "agreement": "same", "close", "different", or "not
            found" (if either score is missing).

    """
    difference = pd.to_numeric(table['difference'], errors = 'coerce').abs()
    agreement = pd.Series('different', index = table.index)
    agreement[difference < _CLOSE] = 'close'
    agreement[difference < _SAME] = 'same'
    agreement[difference.isna()] = 'not found'
    return table.assign(agreement = agreement)


def _replace(
    table: pd.DataFrame,
    rows: pd.Index,
    score: Any,
    source: str) -> None:
    """Puts a published score in rows of a table, in place.

    Args:
        table: a table with "jcs" and "jcs_source".
        rows: the labels of the rows, which may be none.
        score: the published score.
        source: where it came from.

    """
    if len(rows):
        table.loc[rows, 'jcs'] = float(score)
        table.loc[rows, 'jcs_source'] = source


def _words(text: str) -> list[str]:
    """Returns the words of a name, in lower case and without accents.

    Args:
        text: a name.

    Returns:
        Its words, without punctuation ("O'Connor" is "oconnor").

    """
    plain = unicodedata.normalize('NFKD', text)
    plain = plain.encode('ascii', 'ignore').decode().lower()
    plain = plain.replace("'", '').replace('-', ' ')
    return re.sub(r'[^a-z ]', ' ', plain).split()
