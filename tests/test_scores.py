"""Tests for computing the score of each appointment."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from judicial_common_space import fjc, politics, scores


@pytest.fixture
def table(service, demographics):
    return fjc.appointments(service, demographics)


@pytest.fixture
def senate(members, legislators, tmp_path):
    path = tmp_path / 'legislators.json'
    path.write_text(json.dumps(legislators), encoding = 'utf-8')
    return politics.Senate.from_files(members, [path])


@pytest.fixture
def terms(table, martin_quinn):
    return scores.justices(politics.justices(martin_quinn), table, 0)


def _row(scored, nid, sequence = 1):
    found = scored[(scored['nid'] == nid) & (scored['sequence'] == sequence)]
    assert len(found) == 1
    return found.iloc[0]


def test_appointments(table, career, senate, terms) -> None:
    scored = scores.appointments(
        table, fjc.careers(career), senate, terms = terms)
    assert list(scored.columns) == list(scores._COLUMNS)
    doe = _row(scored, 1)
    assert doe['method'] == 'home-state senators'
    assert doe['senators'] == 'MIKULSKI, Barbara; CARDIN, Ben'
    assert doe['jcs'] == pytest.approx(-0.35)
    assert doe['jid'] == 101
    assert doe['congress'] == 112
    elevated = _row(scored, 1, 2)
    assert (elevated['home_state'], elevated['state_source']) == (
        'MD', 'earlier district court')
    assert elevated['jcs'] == pytest.approx(-0.35)
    # Judge Roe is scored by Georgia's senators, and keeps the score when
    # moved to the Eleventh Circuit.
    assert _row(scored, 2)['jcs'] == pytest.approx(-0.075)
    moved = _row(scored, 2, 2)
    assert bool(moved['reassigned'])
    assert moved['jcs'] == pytest.approx(-0.075)
    assert _row(scored, 3)['jcs'] == pytest.approx(0.692)
    assert _row(scored, 3)['method'] == 'president'
    assert _row(scored, 4)['jcs'] == pytest.approx(-0.358)
    assert _row(scored, 4)['state_source'] == 'national court'
    # Renominated by President Bush, Judge Gray gets Virginia's Republicans.
    assert _row(scored, 8)['jcs'] == pytest.approx(0.35)
    # Judge Old left the bench before 1953.
    assert 7 not in scored['nid'].tolist()


def test_appointments_by_date(table, career, senate) -> None:
    by_congress = scores.appointments(table, fjc.careers(career), senate)
    by_date = scores.appointments(
        table, fjc.careers(career), senate, senators = 'date')
    assert _row(by_congress, 6)['jcs'] == pytest.approx(-0.14)
    assert _row(by_congress, 6)['method'] == 'home-state senator'
    assert _row(by_date, 6)['jcs'] == pytest.approx(-0.438)
    assert _row(by_date, 6)['method'] == 'president'


def test_appointments_of_every_year(table, career, senate) -> None:
    scored = scores.appointments(
        table, fjc.careers(career), senate, start_year = None)
    old = _row(scored, 7)
    # Voteview's file here has no score for Franklin Roosevelt.
    assert old['method'] == 'president'
    assert pd.isna(old['jcs'])


def test_justices(table, terms, career, senate) -> None:
    assert terms['title'].tolist() == [
        'Associate Justice', 'Associate Justice', 'Associate Justice',
        'Chief Justice', 'Chief Justice']
    assert terms['sequence'].tolist() == [1, 1, 1, 2, 2]
    assert terms['jid'].tolist() == [105] * 5
    scored = scores.appointments(
        table, fjc.careers(career), senate, terms = terms)
    associate, chief = _row(scored, 5, 1), _row(scored, 5, 2)
    assert associate['method'] == 'Martin-Quinn'
    assert associate['jcs'] == pytest.approx(terms['jcs'].iloc[0])
    assert chief['jcs'] == pytest.approx(terms['jcs'].iloc[3])


def test_justice_numbers_with_the_same_name(table) -> None:
    # Two justices named "J. Smith" are told apart by the number after the
    # name, in the order of their appointments ("JSmith2" is the second).
    court = table[table['court_type'] == 'Supreme Court']
    later = court.assign(
        nid = 9, commission_date = '1990-01-01', first_name = 'Jane')
    both = pd.concat([court, later])
    found = scores._justice_numbers(both, ['JSmith2', 'JPSmith'])
    assert found == {'JSmith2': 9}
