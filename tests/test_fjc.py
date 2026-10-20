"""Tests for reading the Federal Judicial Center's files."""

from __future__ import annotations

import pytest

from judicial_common_space import fjc


def test_appointments(service, demographics) -> None:
    table = fjc.appointments(service, demographics)
    assert len(table) == len(service)
    doe = table[table['nid'] == 1]
    assert doe['jid'].tolist() == [101, 101]
    assert doe['circuit'].isna().tolist() == [True, False]
    assert doe['circuit'].iloc[1] == 4
    assert doe['earlier'].tolist() == [
        (), ('U.S. District Court for the District of Maryland',)]
    assert doe['appointment_date'].tolist() == ['2011-02-01', '2014-03-01']


def test_appointments_of_reassigned_judges(service, demographics) -> None:
    roe = fjc.appointments(service, demographics).query('nid == 2')
    assert roe['reassigned'].tolist() == [False, True]
    assert roe['circuit'].tolist() == [5, 11]
    # The reassignment keeps the president and dates of the appointment.
    assert roe['president'].tolist() == ['Jimmy Carter'] * 2
    assert roe['party'].tolist() == ['Democratic'] * 2
    assert roe['nomination_date'].tolist() == ['1979-05-01'] * 2


def test_appointments_of_reappointed_judges(service, demographics) -> None:
    gray = fjc.appointments(service, demographics).query('nid == 8')
    assert gray['president'].iloc[0] == 'George W. Bush'
    assert gray['party'].iloc[0] == 'Republican'
    assert gray['appointment_date'].iloc[0] == '2001-05-09'


def test_appointment_date_without_a_nomination(service, demographics) -> None:
    service.loc[service['nid'] == '8', 'Nomination Date'] = ''
    gray = fjc.appointments(service, demographics).query('nid == 8')
    assert gray['appointment_date'].iloc[0] == '2000-12-27'


def test_appointments_needs_columns(service, demographics) -> None:
    with pytest.raises(KeyError, match = 'Commission Date'):
        fjc.appointments(
            service.drop(columns = 'Commission Date'), demographics)


def test_careers(career) -> None:
    found = fjc.careers(career)
    assert sorted(found) == [2, 3, 8]
    assert found[2][1] == 'Private practice, Atlanta, Georgia, 1960-1979'
