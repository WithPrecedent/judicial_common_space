"""Tests for the scores of senators, presidents, and justices."""

from __future__ import annotations

import json
import math

import pytest

from judicial_common_space import politics


@pytest.mark.parametrize(('date', 'expected'), [
    ('1933-03-03', 72),
    ('1933-03-04', 73),
    ('1949-01-02', 80),
    ('1949-01-03', 81),
    ('1950-06-01', 81),
    ('2021-01-03', 117),
    ('2022-12-31', 117)])
def test_congress(date: str, expected: int) -> None:
    assert politics.congress(date) == expected


@pytest.fixture
def senate(members, legislators, tmp_path) -> politics.Senate:
    path = tmp_path / 'legislators.json'
    path.write_text(json.dumps(legislators), encoding = 'utf-8')
    return politics.Senate.from_files(members, [path])


def test_senators_by_congress_and_by_date(senate) -> None:
    both = [('MIKULSKI, Barbara', -0.4), ('CARDIN, Ben', -0.3)]
    assert senate.senators('MD', '2011-02-01', 'Democratic') == both
    assert senate.senators('MD', '2011-02-01', 'Democratic', 'date') == both
    assert senate.senators('MD', '2011-02-01', 'Republican') == []
    # Campbell was a Democrat in the 104th Congress until March 3, 1995.
    assert senate.senators('CO', '1995-03-31', 'Democratic') == [
        ('CAMPBELL, Ben', -0.14)]
    assert senate.senators('CO', '1995-03-31', 'Democratic', 'date') == []
    assert senate.senators('CO', '1995-03-31', 'Republican', 'date') == [
        ('BROWN, Hank', 0.4), ('CAMPBELL, Ben', 0.2)]
    assert senate.senators('CO', '1995-02-01', 'Democratic', 'date') == [
        ('CAMPBELL, Ben', -0.14)]
    with pytest.raises(ValueError, match = 'how must be'):
        senate.senators('MD', '2011-02-01', 'Democratic', 'year')


def test_president(senate) -> None:
    assert senate.president('Barack Obama') == -0.358
    assert senate.president('Herbert Hoover') is None
    assert senate.president('Somebody Else') is None


def test_justices(martin_quinn) -> None:
    scores = politics.justices(martin_quinn)
    expected = 2 / math.pi * math.atan(0.1934 + 0.6025 * 3.0)
    assert scores['jcs'].iloc[0] == pytest.approx(expected)
    assert list(scores.columns) == [
        'term', 'justice', 'justiceName', 'martin_quinn', 'jcs']
    paper = politics.justices(martin_quinn, 'paper')
    expected = 2 / math.pi * math.atan(-0.1736 + 0.461 * 3.0)
    assert paper['jcs'].iloc[0] == pytest.approx(expected)
    custom = politics.justices(martin_quinn, (0.0, 0.0))
    assert (custom['jcs'] == 0).all()
    with pytest.raises(ValueError, match = 'transformation'):
        politics.justices(martin_quinn, 'unknown')
    with pytest.raises(KeyError, match = 'post_mn'):
        politics.justices(martin_quinn.drop(columns = 'post_mn'))
