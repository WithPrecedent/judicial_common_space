"""Computes the Judicial Common Space score of each appointment.

Epstein, Martin, Segal, and Westerland ("The Judicial Common Space," 23
J.L. Econ. & Org. 303 (2007)) score judges of the lower federal courts by
Giles, Hettinger, and Peppers's rule, which follows the norm of senatorial
courtesy: if a judge is appointed from a state where the president and at
least one senator are of the same party, the judge gets that senator's
NOMINATE score (or the mean of the senators' scores, if more than one is of
the president's party). Otherwise, the judge gets the president's score.
Justices of the Supreme Court get their Martin-Quinn scores, put on the same
scale (see `politics.justices`).

So a judge's score belongs to an appointment: a district judge who is
elevated to a court of appeals is scored again, by the president and
senators of the second appointment. `appointments` scores every appointment
to a federal court of a judge who served on it in or after a year (by
default 1953, the first year of Epstein et al.'s study). A judge moved to a court without an appointment (as when the
Eleventh Circuit was made from the Fifth) keeps the score of the
appointment before.

Contents:
    appointments: returns the score of each appointment.
    justices: returns each justice's score in each term, with the
        Federal Judicial Center's numbers for the justice.
    _COLUMNS: the columns of `appointments`.

"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any, cast

import pandas as pd

from . import options, politics, states

logger = logging.getLogger(__name__)

_COLUMNS: tuple[str, ...] = (
    'judge', 'nid', 'jid', 'court_type', 'court', 'circuit', 'title',
    'sequence', 'president', 'party', 'nomination_date', 'recess_date',
    'commission_date', 'termination_date', 'appointment_date', 'congress',
    'reassigned', 'home_state', 'state_source', 'duty_station', 'method',
    'senators', 'president_score', 'jcs')


def appointments(
    table: pd.DataFrame,
    careers: Mapping[int, Sequence[str]],
    senate: politics.Senate,
    *,
    start_year: int | None = options._START_YEAR,
    senators: str = 'congress',
    terms: pd.DataFrame | None = None) -> pd.DataFrame:
    """Returns the score of each appointment.

    | Column | Meaning |
    | --- | --- |
    | `judge`, `nid`, `jid` | The judge's name and the Federal Judicial Center's two numbers for the judge. |
    | `court_type`, `court`, `circuit`, `title`, `sequence` | The court, the judge's title on it, and the order of the appointment among the judge's (see `fjc.appointments`). |
    | `president`, `party` | The president who appointed the judge, and that president's party. |
    | `nomination_date`, `recess_date`, `commission_date`, `termination_date` | Dates of the appointment and of the end of the judge's service on the court. |
    | `appointment_date`, `congress` | The day that the senators and president are found on (see `fjc.appointments`), and the Congress that sat then. |
    | `reassigned` | Whether the judge was moved to the court without an appointment, and so keeps the score of the appointment before. |
    | `home_state`, `state_source` | The state that the judge was appointed from (a postal code), and how it was found (see `states.home_state`). |
    | `duty_station` | For a judge of a court of appeals, the state where Wikipedia says the judge sat (see `stations`), which is used for `home_state` only when the judge's career shows none. |
    | `method` | How the score was found: "home-state senator", "home-state senators", "president", or "Martin-Quinn". |
    | `senators` | The senators whose scores were used, separated by semicolons. |
    | `president_score` | The president's score. |
    | `jcs` | The Judicial Common Space score. A justice's score is that of the first term of the appointment (`justices` has every term). Missing if there is no score (as for Herbert Hoover, whom Voteview does not score, or a justice without Martin-Quinn scores). |

    Args:
        table: the appointments (see `fjc.appointments`), with the states of
            the judges' duty stations as "duty_station" if they are known
            (see `stations.match`).
        careers: the entries of each judge's career, by the judge's "nid"
            (see `fjc.careers`).
        senate: the scores of senators and presidents.
        start_year: the first year of service to include: an appointment is
            included if the judge was serving on the court in that year or
            later. Defaults to 1953. `None` includes every appointment.
        senators: "congress" or "date": which senators count (see
            `politics.Senate.senators`). Defaults to "congress", as in the
            published Judicial Common Space scores.
        terms: the justices' scores in each term (see `justices`). Defaults
            to `None`, in which case the justices have no scores.

    Returns:
        The table, sorted by the judges' names and the order of their
            appointments.

    """
    first_terms = {} if terms is None else _first_terms(terms)
    rows: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    records = cast('list[dict[str, Any]]', table.to_dict('records'))
    for record in records:
        if previous is not None and previous['nid'] != record['nid']:
            previous = None
        row = {column: record.get(column) for column in _COLUMNS}
        date = str(record['appointment_date'] or '')
        row['congress'] = politics.congress(date) if date else None
        if record['reassigned'] and previous is not None:
            for column in (
                'home_state', 'state_source', 'method', 'senators',
                'president_score', 'jcs'):
                row[column] = previous[column]
        else:
            row.update(_score(record, careers, senate, senators, first_terms))
        rows.append(row)
        previous = row
    scored = pd.DataFrame(rows, columns = list(_COLUMNS))
    if start_year is not None:
        first = f'{start_year}-01-01'
        serving = (scored['termination_date'] == '') | (
            scored['termination_date'] >= first)
        scored = scored[serving]
    scored = scored.sort_values(['judge', 'nid', 'sequence'], kind = 'stable')
    scored = scored.astype({
        'circuit': 'Int64', 'sequence': 'Int64', 'congress': 'Int64',
        'jcs': 'Float64', 'president_score': 'Float64'})
    return scored.reset_index(drop = True)


def justices(
    terms: pd.DataFrame,
    table: pd.DataFrame,
    start_year: int = options._START_YEAR) -> pd.DataFrame:
    """Returns each justice's score in each term, with the center's numbers.

    Each justice of the Martin-Quinn scores is found among the Supreme Court
    appointments of `table` by the justice's last name and initials (the
    Supreme Court Database names justices like "WHRehnquist"). A term belongs
    to the justice's last appointment that was commissioned by the end of
    the term (the June after it began), so William Rehnquist's terms from
    1986 are those of his appointment as Chief Justice.

    Args:
        terms: the justices' scores in each term (see `politics.justices`).
        table: the appointments (see `fjc.appointments`).
        start_year: the first term to include. Defaults to 1953.

    Returns:
        A table with "term", "justiceName", "judge", "nid", "jid", "title"
            (the justice's title in the term), "sequence" (of the
            appointment), "martin_quinn", and "jcs".

    """
    court = table[table['court_type'] == 'Supreme Court']
    found = _justice_numbers(
        court, [str(name) for name in terms['justiceName'].unique()])
    rows = []
    for record in terms.to_dict('records'):
        term = record['term']
        nid = found.get(record['justiceName'])
        if term is None or pd.isna(term) or int(term) < start_year:
            continue
        appointment = None
        if nid is not None:
            served = court[
                (court['nid'] == nid)
                & (court['commission_date'] != '')
                & (court['commission_date'] <= f'{int(term) + 1}-06-30')]
            if len(served):
                appointment = served.iloc[-1]
        rows.append({
            'term': int(term),
            'justiceName': record['justiceName'],
            'judge': None if appointment is None else appointment['judge'],
            'nid': nid,
            'jid': None if appointment is None else appointment['jid'],
            'title': None if appointment is None else appointment['title'],
            'sequence': (
                None if appointment is None else appointment['sequence']),
            'martin_quinn': record['martin_quinn'],
            'jcs': record['jcs']})
    result = pd.DataFrame(rows)
    if result.empty:
        return result
    result = result.astype({'nid': 'Int64', 'jid': 'Int64', 'sequence': 'Int64'})
    return result.sort_values(['term', 'justiceName']).reset_index(drop = True)


""" Private Functions """


def _first_terms(terms: pd.DataFrame) -> dict[tuple[int, int], float]:
    """Returns the score of each justice's appointment in its first term.

    Args:
        terms: a table made by `justices`.

    Returns:
        The score of the first term of each appointment, by the justice's
            "nid" and the appointment's "sequence".

    """
    if terms.empty:
        return {}
    known = terms.dropna(subset = ['nid', 'sequence']).sort_values('term')
    first = known.drop_duplicates(['nid', 'sequence'])
    return {
        (int(nid), int(sequence)): float(score)
        for nid, sequence, score in zip(
            first['nid'], first['sequence'], first['jcs'], strict = True)}


def _justice_numbers(
    court: pd.DataFrame,
    names: Sequence[str]) -> dict[str, int]:
    """Returns the center's number for each justice of the Martin-Quinn scores.

    Args:
        court: the appointments to the Supreme Court (see
            `fjc.appointments`).
        names: the Supreme Court Database's names of the justices, such as
            "SDOConnor" and "JHarlan2".

    Returns:
        The "nid" of each justice who was found, by the justice's name.

    """
    # Justices with the same name (John Marshall Harlan and his grandson) are
    # numbered by the order of their appointments, as "JHarlan2".
    people = court.sort_values('commission_date').drop_duplicates('nid')
    found = {}
    for name in names:
        bare = re.sub(r'\d+$', '', str(name))
        number = str(name)[len(bare):]
        fits = []
        for person in people.to_dict('records'):
            last = re.sub(r'[^A-Za-z]', '', str(person['last_name']))
            if not last or not bare.lower().endswith(last.lower()):
                continue
            initials = bare[:len(bare) - len(last)]
            given = f"{person['first_name']} {person['middle_name']}".split()
            if not initials or initials[0].upper() == given[0][0].upper():
                fits.append(int(person['nid']))
        if len(fits) > 1 and number and int(number) <= len(fits):
            fits = [fits[int(number) - 1]]
        if len(fits) == 1:
            found[str(name)] = fits[0]
        else:
            logger.info(
                'the justice %s was not found among the Supreme Court '
                'appointments', name)
    return found


def _score(
    record: Mapping[str, Any],
    careers: Mapping[int, Sequence[str]],
    senate: politics.Senate,
    how: str,
    first_terms: Mapping[tuple[int, int], float]) -> dict[str, Any]:
    """Returns the score of one appointment and how it was found.

    Args:
        record: a row of `fjc.appointments`.
        careers: the entries of each judge's career, by the judge's "nid".
        senate: the scores of senators and presidents.
        how: which senators count ("congress" or "date").
        first_terms: the scores of the justices' appointments in their first
            terms, by "nid" and "sequence".

    Returns:
        The values of "home_state", "state_source", "method", "senators",
            "president_score", and "jcs".

    """
    president = senate.president(str(record['president']))
    state, source = states.home_state(record, careers.get(int(record['nid']), ()))
    result: dict[str, Any] = {
        'home_state': state, 'state_source': source, 'senators': '',
        'president_score': president}
    if record['court_type'] == 'Supreme Court':
        key = (int(record['nid']), int(record['sequence']))
        return {**result, 'method': 'Martin-Quinn', 'jcs': first_terms.get(key)}
    found = []
    if state and state not in options._TERRITORIES:
        found = senate.senators(
            state, str(record['appointment_date']), str(record['party']),
            how = how)
    if not found:
        return {**result, 'method': 'president', 'jcs': president}
    method = 'home-state senator' if len(found) == 1 else 'home-state senators'
    return {
        **result,
        'method': method,
        'senators': '; '.join(name for name, _ in found),
        'jcs': sum(score for _, score in found) / len(found)}
