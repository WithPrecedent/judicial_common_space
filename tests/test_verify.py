"""Tests for comparing the scores with published scores."""

from __future__ import annotations

import pandas as pd
import pytest

from judicial_common_space import verify


def _court(*names: str) -> pd.DataFrame:
    return pd.DataFrame({
        'nid': list(range(1, len(names) + 1)), 'judge': list(names)})


@pytest.mark.parametrize(('name', 'judges', 'expected'), [
    ('Coney Barrett, Amy', ('Barrett, Amy Coney', 'Sykes, Diane'), 1),
    ('Kerner, Otto, Jr.', ('Kerner, Otto', 'Kerner, Otto, Jr.'), 2),
    ('Johnson, Sam D.', ('Johnson, Frank', 'Johnson, Samuel D., Jr.'), 2),
    ("O'Connor, Sandra", ("O'Connor, Sandra Day",), 1),
    ('Van Oosterhout, Martin D.', ('Van Oosterhout, Martin Donald',), 1),
    ('Wilkinson, J. Harvie', ('Wilkinson, James Harvie, III',), 1),
    ('Smith, Jerry', ('Smith, Jerry E.', 'Smith, Jerry Edwin'), None)])
def test_match_name(
    name: str,
    judges: tuple[str, ...],
    expected: int | None) -> None:
    assert verify.match_name(name, _court(*judges)) == expected


def _scored() -> pd.DataFrame:
    return pd.DataFrame({
        'nid': [1, 2, 3],
        'judge': ['Doe, Jane', 'Roe, Richard', 'Poe, Edgar'],
        'court_type': ['U.S. Court of Appeals'] * 2 + ['U.S. District Court'],
        'court': ['', '', 'U.S. District Court for the District of Maryland'],
        'circuit': [4, 9, None],
        'sequence': [1, 1, 1],
        'reassigned': [False] * 3,
        'jcs': [-0.35, 0.3, 0.1],
        **{column: [''] * 3 for column in verify._DETAILS}})


def test_circuit_judges() -> None:
    published = pd.DataFrame({
        'name': ['Doe, Jane', 'Roe, Richard', 'Nobody, Ned'],
        'circuit': [4, 9, 9],
        'jcs': [-0.35, 0.31, 0.2]})
    check = verify.circuit_judges(_scored(), published)
    assert check['agreement'].tolist() == ['same', 'close', 'not found']
    assert check['nid'].tolist()[:2] == [1, 2]
    assert check['difference'].iloc[1] == pytest.approx(-0.01)


def test_district_judges() -> None:
    published = pd.DataFrame({
        'nid': [3, 4], 'judgename': ['Poe, Edgar', 'Nobody, Ned'],
        'ideology_score': [0.2, 0.1]})
    check = verify.district_judges(_scored(), published)
    assert check['agreement'].tolist() == ['different', 'not found']


def test_justices() -> None:
    terms = pd.DataFrame({
        'term': [2020], 'justiceName': ['ACBarrett'], 'judge': ['Barrett'],
        'nid': [9], 'jcs': [0.4251]})
    published = pd.DataFrame({
        'term': ['2020', '2021'], 'justiceName': ['ACBarrett'] * 2,
        'jcs': [0.4252, 0.43]})
    check = verify.justices(terms, published)
    assert check['agreement'].tolist() == ['same', 'not found']


def test_mark_computed() -> None:
    marked = verify.mark_computed(_scored())
    columns = list(marked.columns)
    assert columns[columns.index('jcs') - 1] == 'computed_jcs'
    assert columns[columns.index('jcs') + 1] == 'jcs_source'
    assert (marked['jcs_source'] == 'computed').all()
    # A table that has them, or has no scores, is only copied.
    assert verify.mark_computed(marked).equals(marked)
    assert verify.mark_computed(pd.DataFrame()).empty


def test_use_published() -> None:
    circuit = pd.DataFrame({
        'nid': [1, 2], 'circuit': [4, 9], 'published': [-0.2, 0.33],
        'difference': [-0.15, -0.03]})
    district = pd.DataFrame({
        'nid': [3], 'published': [0.4], 'difference': [-0.3]})
    terms = pd.DataFrame({
        'term': [2020, 2021], 'justiceName': ['ACBarrett'] * 2,
        'nid': [9, 9], 'sequence': [1, 1], 'jcs': [0.17, 0.18]})
    justices = pd.DataFrame({
        'term': [2020], 'justiceName': ['ACBarrett'], 'published': [0.43],
        'difference': [-0.26]})
    scored = pd.concat([_scored(), pd.DataFrame({
        'nid': [9], 'judge': ['Barrett, Amy'], 'court_type': ['Supreme Court'],
        'court': [''], 'circuit': [None], 'sequence': [1],
        'reassigned': [False], 'jcs': [0.17]})], ignore_index = True)
    checks = {
        'circuit_judges': circuit, 'district_judges': district,
        'justices': justices}
    replaced, replaced_terms = verify.use_published(scored, terms, checks)
    # Judge Roe's score differs by less than 0.05, so is kept.
    assert replaced['jcs'].tolist() == [-0.2, 0.3, 0.4, 0.43]
    assert replaced['computed_jcs'].tolist() == [-0.35, 0.3, 0.1, 0.17]
    assert replaced['jcs_source'].tolist() == [
        'Epstein et al.', 'computed', 'Boyd', 'Epstein et al.']
    assert replaced_terms['jcs'].tolist() == [0.43, 0.18]
    assert replaced_terms['jcs_source'].tolist() == [
        'Epstein et al.', 'computed']
    # A larger threshold keeps more of the computed scores.
    kept, _ = verify.use_published(scored, terms, checks, threshold = 0.2)
    assert kept['jcs_source'].tolist() == [
        'computed', 'computed', 'Boyd', 'Epstein et al.']
    nothing, _ = verify.use_published(scored, terms, {})
    assert (nothing['jcs_source'] == 'computed').all()


def test_summarize() -> None:
    check = pd.DataFrame({
        'published': [0.1, 0.2, 0.3, 0.4],
        'computed': [0.1, 0.21, 0.5, None],
        'difference': [0.0, 0.01, 0.2, None]})
    summary = verify.summarize({'check': verify._finish(check)})
    row = summary.iloc[0]
    assert (row['published'], row['found']) == (4, 3)
    assert (row['same'], row['close'], row['different']) == (1, 1, 1)
    assert row['share_same_or_close'] == pytest.approx(2 / 3)
