"""Tests for finding the state that each judge was appointed from."""

from __future__ import annotations

import pytest

from judicial_common_space import states


@pytest.mark.parametrize(('entry', 'expected'), [
    ('Private practice, Kansas City, Missouri, 1970-1980', ['MO']),
    ('Private practice, Delaware County, Pennsylvania, 1970-1980', ['PA']),
    ('Office of the Federal Public Defender for the Districts of Colorado and '
     'Wyoming, 2002-2021', ['CO', 'WY']),
    ('Faculty, University of Chicago Law School, 1969-', ['IL']),
    ('Private practice, Washington, D.C., 1990-2000', ['DC']),
    ('Professor, George Washington University Law School, 1990-2000', ['DC']),
    ('Professor, Washington University School of Law, 1990-2000', ['MO']),
    ('Professor, Washington and Lee University, 1990-2000', ['VA']),
    ('Judge, West Virginia Supreme Court of Appeals, 1990-2000', ['WV']),
    ('Private practice, Seattle, Washington, 1990-2000', ['WA']),
    ('Assistant U.S. attorney, Northern District of Illinois, U.S. '
     'Department of Justice, 1990-2000', ['IL', 'DC']),
    ('U.S. Army lieutenant, 1943-1946', [])])
def test_places(entry: str, expected: list[str]) -> None:
    assert states.places(entry) == expected


@pytest.mark.parametrize(('entry', 'expected'), [
    ('Private practice, Albuquerque, New Mexico, 1983-1987, 1988-2003',
     (1983, 2003)),
    ('Adjunct faculty member, University of Iowa College of Law, 2014-',
     (2014, None)),
    ('Rhode Island public defender, 2020-present', (2020, None)),
    ('Chief, Executive Office for United States Attorneys, 1953',
     (1953, 1953)),
    ('Harvard Law School, 1999-2014; assistant professor, 1999-2004',
     (1999, 2014)),
    ('Law clerk to a judge', (None, None))])
def test_span(entry: str, expected: tuple[int | None, int | None]) -> None:
    assert states._span(entry) == expected


def test_career_state_prefers_the_job_held_when_appointed() -> None:
    entries = [
        'Associate justice, Minnesota Supreme Court, 2010-2018',
        'Visiting professor, Vanderbilt University Law School, 2012',
        'Adjunct faculty member, University of Iowa College of Law, 2014-',
        'Private practice, Washington, D.C., 2001-2002']
    assert states.career_state(entries, 2018) == 'MN'
    # Only the states of the circuit count.
    assert states.career_state(entries, 2018, ['IA', 'TN']) == 'IA'
    assert states.career_state(entries, 2018, ['TN']) == 'TN'
    assert states.career_state(entries, 2018, ['TN'], past = False) is None
    # Jobs that began after the appointment do not count.
    assert states.career_state(entries, 2005) == 'DC'


def _appointment(court: str, **values: object) -> dict[str, object]:
    kind = (
        'U.S. District Court' if court.startswith('U.S. District')
        else 'U.S. Court of Appeals')
    circuit = None
    for words, number in (
        ('Fourth', 4), ('Fifth', 5), ('Eleventh', 11),
        ('District of Columbia Circuit', 12), ('Federal', 13)):
        if words in court and kind == 'U.S. Court of Appeals':
            circuit = number
    return {
        'court': court, 'court_type': kind, 'circuit': circuit,
        'appointment_date': '2001-01-01', 'earlier': (), 'birth_state': '',
        **values}


def test_home_state_of_district_judges() -> None:
    appointment = _appointment(
        'U.S. District Court for the Middle District of Georgia')
    assert states.home_state(appointment) == ('GA', 'court')
    appointment = _appointment('U.S. District Court for the District of '
                               'Columbia')
    assert states.home_state(appointment) == ('DC', 'court')


def test_home_state_of_judges_of_courts_of_appeals() -> None:
    fourth = 'U.S. Court of Appeals for the Fourth Circuit'
    earlier = (
        'U.S. District Court for the District of Maryland',
        'U.S. District Court for the Southern District of New York')
    # The last district court in the circuit, not the last one.
    assert states.home_state(_appointment(fourth, earlier = earlier)) == (
        'MD', 'earlier district court')
    career = ['Private practice, Richmond, Virginia, 1980-2000']
    assert states.home_state(_appointment(fourth), career) == ('VA', 'career')
    career = ['Private practice, Boston, Massachusetts, 1980-2000']
    assert states.home_state(
        _appointment(fourth, birth_state = 'NC'), career) == (
            'NC', 'birth state')
    assert states.home_state(_appointment(fourth), career) == (
        None, 'not found')


def test_home_state_before_the_eleventh_circuit() -> None:
    fifth = 'U.S. Court of Appeals for the Fifth Circuit'
    career = ['Private practice, Atlanta, Georgia, 1960-1979']
    before = _appointment(fifth, appointment_date = '1979-05-01')
    after = _appointment(fifth, appointment_date = '1985-05-01')
    assert states.home_state(before, career) == ('GA', 'career')
    assert states.home_state(after, career) == (None, 'not found')


def test_home_state_of_judges_without_one() -> None:
    dc = _appointment(
        'U.S. Court of Appeals for the District of Columbia Circuit',
        earlier = ('U.S. District Court for the District of South Carolina',))
    assert states.home_state(dc) == ('DC', 'court')
    federal = _appointment('U.S. Court of Appeals for the Federal Circuit')
    assert states.home_state(federal) == (None, 'national court')
    trade = {
        'court': 'U.S. Court of International Trade', 'court_type': 'Other',
        'circuit': None}
    assert states.home_state(trade) == (None, 'national court')
    justice = {
        'court': 'Supreme Court of the United States',
        'court_type': 'Supreme Court', 'circuit': None}
    assert states.home_state(justice) == (None, 'Supreme Court')
