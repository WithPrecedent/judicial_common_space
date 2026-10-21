"""Finds the state that each judge was appointed from.

Giles, Hettinger, and Peppers's rule gives a judge the scores of the
senators of the judge's home state, so each appointment needs a state. The
Federal Judicial Center's files name it for a district judge (in the
court's name), but not for a judge of a court of appeals, which serves
several states. Its place is found from the judge's record, in this order:

1. The state of a district court that the judge served on before, if it is
   in the circuit.
2. The judge's career before the appointment (see `career_state`): the jobs
   that the judge held when appointed come first, then the most recent jobs
   before. A job's place is the first state that its entry names (as in
   "Federal Public Defender for the Districts of Colorado and Wyoming"), not
   counting cities and counties named for states ("Kansas City, Missouri"),
   or else the state of a city or school that it names without one (as
   "Harvard Law School"; see `options._PLACES`). Only states of the circuit
   count.
3. The state of the judge's duty station, as Wikipedia's article on the
   court gives it (see `stations`), if it is in the circuit. It comes after
   the judge's career because it is where the judge sat, which is sometimes
   not where the judge came from (Alfred Goodwin came from Oregon's
   district court and sat in California).
4. The state where the judge was born, if it is in the circuit.

Judges of the District of Columbia Circuit have the District of Columbia,
which has no senators, so they get the score of the president, as all but
three of them do in the published Judicial Common Space scores (even those
who came from district courts in states). Judges of courts with national
jurisdiction (the Federal Circuit, the Court of International Trade, and the
courts before them) have no home state, so they get the score of the
president too, as the Federal Circuit's judges do in the published scores.

Contents:
    career_state: returns the state of a judge's career before an
        appointment.
    home_state: returns the state that a judge was appointed from, and how
        it was found.
    places: returns the states that a career entry names.

"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from . import options

_ABBREVIATIONS: dict[str, str] = {
    name: code for code, name in options._STATES.items()}
_DISTRICT: re.Pattern[str] = re.compile(
    r'Districts? of ([A-Za-z ]+?)\s*(?:\(|$)')
# Longer names come first, so "West Virginia" is not read as "Virginia".
_NAMES: re.Pattern[str] = re.compile(
    r'\b(' + '|'.join(sorted(
        (name for code, name in options._STATES.items() if code != 'DC'),
        key = len, reverse = True)) + r')\b')
# A state's name followed by these is the name of a city or a county, which
# may be in another state ("Kansas City, Missouri", "Delaware County,
# Pennsylvania").
_NOT_A_STATE: re.Pattern[str] = re.compile(
    r'\s+(City|County|Parish|Township|River|Avenue|Street)\b')
# Places that contain the name of a state they are not in.
_NOT_THEIR_STATES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r'\bWashington and Lee\b'), 'VA'),
    (re.compile(r'\bWashington College of Law\b'), 'DC'))
_YEARS: re.Pattern[str] = re.compile(
    r'\b(\d{4})(?:\s*(-)\s*(\d{4}|present)?)?')


def career_state(
    entries: Sequence[str],
    year: int,
    allowed: Iterable[str] | None = None,
    *,
    past: bool = True) -> str | None:
    """Returns the state of a judge's career before an appointment.

    The jobs that the judge held in the year of the appointment come first
    (the most recent first, and minor ones such as visiting professorships
    last), then the jobs that had ended (the most recent first).

    Args:
        entries: the entries of the judge's career (see `fjc.careers`).
        year: the year of the appointment.
        allowed: the states that count. Defaults to `None`, for all of them.
        past: whether jobs that had ended by the appointment count.
            Defaults to `True`.

    Returns:
        The postal code of the state, or `None` if no entry names one that
            counts.

    """
    permitted = None if allowed is None else set(allowed)
    current: list[tuple[int, str]] = []
    minor: list[tuple[int, str]] = []
    ended: list[tuple[int, int, str]] = []
    for entry in entries:
        start, end = _span(entry)
        if start is None or start > year:
            continue
        if end is None or end >= year:
            if options._MINOR_POSITIONS.match(entry):
                minor.append((start, entry))
            else:
                current.append((start, entry))
        else:
            ended.append((end, start, entry))
    ordered = (
        [entry for _, entry in sorted(current, key = lambda x: -x[0])]
        + [entry for _, entry in sorted(minor, key = lambda x: -x[0])])
    if past:
        ordered += [
            entry for _, _, entry in sorted(
                ended, key = lambda x: (-x[0], -x[1]))]
    for entry in ordered:
        for state in places(entry):
            if permitted is None or state in permitted:
                return state
    return None


def home_state(
    appointment: Mapping[str, Any],
    career: Sequence[str] = ()) -> tuple[str | None, str]:
    """Returns the state that a judge was appointed from, and how it was found.

    Args:
        appointment: a row of `fjc.appointments`, with the state of the
            judge's duty station as "duty_station" if it is known (see
            `stations.match`).
        career: the entries of the judge's career (see `fjc.careers`).

    Returns:
        The postal code of the state (`None` if there is none), and how it
            was found: "court" (the court's name), "earlier district court",
            "career", "duty station", "birth state", "national court",
            "Supreme Court", or "not found".

    """
    court = str(appointment['court'])
    court_type = str(appointment['court_type'])
    if court_type == 'U.S. District Court':
        return _district_state(court), 'court'
    if court_type == 'Supreme Court':
        return None, 'Supreme Court'
    try:
        circuit: int | None = int(appointment.get('circuit'))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        circuit = None
    national = any(name in court for name in options._NATIONAL_COURTS)
    if circuit is None or circuit == 13 or national:
        return None, 'national court'
    date = str(appointment.get('appointment_date') or '')
    year = int(date[:4]) if date else 9999
    if circuit == 12:
        return 'DC', 'court'
    if circuit == 5 and date and date < options._SPLIT_FIFTH:
        allowed = options._OLD_FIFTH
    else:
        allowed = options._CIRCUIT_STATES[circuit]
    for earlier in reversed(list(appointment.get('earlier') or ())):
        state = _district_state(str(earlier))
        if state and state in allowed:
            return state, 'earlier district court'
    state = career_state(career, year, allowed)
    if state:
        return state, 'career'
    station = str(appointment.get('duty_station') or '')
    if station in allowed:
        return station, 'duty station'
    birth = str(appointment.get('birth_state') or '')
    if birth in allowed:
        return birth, 'birth state'
    return None, 'not found'


def places(entry: str) -> list[str]:
    """Returns the states that a career entry names.

    Args:
        entry: an entry of a judge's career.

    Returns:
        The postal codes of the states, most likely first: the states that
            the entry names, in its order (leaving out names of cities and
            counties, as in "Kansas City, Missouri"); then the states of
            cities and schools that it names without their states; then "DC"
            if it names Washington, D.C., or a job that is there (see
            `options._DC_AGENCIES`).

    """
    text = entry
    capital = False
    for pattern in (options._DC_PLACES, options._DC_AGENCIES):
        if pattern.search(text):
            capital = True
            text = pattern.sub(' ', text)
    implied: list[tuple[int, str]] = []
    for pattern, state in (*_NOT_THEIR_STATES, *options._PLACES):
        for match in pattern.finditer(text):
            implied.append((match.start(), state))
        text = pattern.sub(lambda match: ' ' * len(match.group()), text)
    named = [
        _ABBREVIATIONS[match.group(1)] for match in _NAMES.finditer(text)
        if not _NOT_A_STATE.match(text, match.end())]
    found = named + [state for _, state in sorted(implied)]
    if capital:
        found.append('DC')
    return list(dict.fromkeys(found))


""" Private Functions """


def _district_state(court: str) -> str | None:
    """Returns the state of a district court.

    Args:
        court: the court's name, such as "U.S. District Court for the Middle
            District of Georgia".

    Returns:
        The state's postal code ("DC" for the District of Columbia), or
            `None` if the name has no state.

    """
    match = _DISTRICT.search(court)
    if not match:
        return None
    name = match.group(1).strip()
    if name == 'Columbia':
        return 'DC'
    return _ABBREVIATIONS.get(name)


def _span(entry: str) -> tuple[int | None, int | None]:
    """Returns the first and last years of a career entry.

    The years of the whole job come before the first semicolon (those after
    it are of positions within the job).

    Args:
        entry: an entry of a judge's career, such as "Private practice,
            Albuquerque, New Mexico, 1983-1987, 1988-2003".

    Returns:
        The first year and the last year (`None` if the job continued, as
            in "2014-" or "2014-present"), or `None` for both if the entry
            has no year.

    """
    head = entry.split(';', 1)[0]
    found = _YEARS.findall(head) or _YEARS.findall(entry)
    if not found:
        return None, None
    starts = [int(start) for start, _, _ in found]
    ends = [
        None if dash and end in ('', 'present')
        else int(end) if dash else int(start)
        for start, dash, end in found]
    if None in ends:
        return min(starts), None
    return min(starts), max(end for end in ends if end is not None)
