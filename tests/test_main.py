"""Tests for computing, checking, and saving the scores."""

from __future__ import annotations

import pandas as pd
import pytest

import judicial_common_space
from judicial_common_space import __main__ as cli
from judicial_common_space import sources


def test_run(data_folder, tmp_path) -> None:
    path = judicial_common_space.run(
        tmp_path / 'scores.xlsx', folder = data_folder, download = False)
    sheets = pd.read_excel(path, sheet_name = None)
    assert list(sheets) == [
        'Scores', 'Justices', 'Verification', 'Circuit check',
        'District check', 'Justice check', 'About']
    scores = sheets['Scores']
    assert {'judge', 'nid', 'jid', 'jcs'} <= set(scores.columns)
    assert 7 not in scores['nid'].tolist()
    lutt = scores.query('nid == 9').iloc[0]
    assert (lutt['home_state'], lutt['state_source']) == ('VA', 'duty station')
    assert lutt['duty_station'] == 'VA'
    assert lutt['jcs'] == pytest.approx(0.3)
    summary = sheets['Verification'].set_index('check')
    assert summary.loc['circuit_judges', 'found'] == 4
    assert summary.loc['circuit_judges', 'same'] == 3
    assert summary.loc['district_judges', 'same'] == 1
    assert 'senators: congress' in sheets['About']['About'].tolist()


def test_run_with_published_scores(data_folder, tmp_path) -> None:
    default = judicial_common_space.run(
        tmp_path / 'default.xlsx', folder = data_folder, download = False)
    scores = pd.read_excel(default, sheet_name = 'Scores')
    assert (scores['jcs_source'] == 'computed').all()
    assert scores['jcs'].equals(scores['computed_jcs'])
    path = judicial_common_space.run(
        tmp_path / 'published.xlsx', folder = data_folder, download = False,
        use_published = True)
    sheets = pd.read_excel(path, sheet_name = None)
    scores = sheets['Scores'].set_index(['nid', 'sequence'])
    # The published file gives Judge Poe 0.5, and the computed score is the
    # president's, 0.692.
    assert scores.loc[(3, 1), 'jcs'] == pytest.approx(0.5)
    assert scores.loc[(3, 1), 'computed_jcs'] == pytest.approx(0.692)
    assert scores.loc[(3, 1), 'jcs_source'] == 'Epstein et al.'
    # Boyd's score of Judge Green differs from the computed one by 0.298.
    assert scores.loc[(6, 1), 'jcs'] == pytest.approx(-0.438)
    assert scores.loc[(6, 1), 'jcs_source'] == 'Boyd'
    # Judge Doe's scores match, so they are computed.
    assert scores.loc[(1, 1), 'jcs_source'] == 'computed'
    # Each of Justice Smith's appointments gets its first term's score.
    assert scores.loc[(5, 1), 'jcs'] == pytest.approx(0.0)
    assert scores.loc[(5, 2), 'jcs'] == pytest.approx(0.0)
    justices = sheets['Justices']
    assert justices['jcs_source'].tolist() == [
        'Epstein et al.', 'computed', 'computed', 'Epstein et al.',
        'computed']
    # The checks compare the computed scores.
    summary = sheets['Verification'].set_index('check')
    assert summary.loc['circuit_judges', 'same'] == 3
    about = sheets['About']['About'].tolist()
    assert 'use_published: True (threshold 0.05)' in about


def test_run_starts_with_the_term_sitting_in_january(
    data_folder,
    tmp_path) -> None:
    path = judicial_common_space.run(
        tmp_path / 'scores.xlsx', folder = data_folder, download = False,
        start_year = 1973, check = False)
    justices = pd.read_excel(path, sheet_name = 'Justices')
    # The 1972 term was sitting in January 1973; the 1971 term was not.
    assert justices['term'].tolist() == [1972, 1985, 1986, 1987]


def test_run_without_optional_files(data_folder, tmp_path) -> None:
    found = sources.paths(data_folder)
    found['martin_quinn'].unlink()
    found['duty_stations'].unlink()
    path = judicial_common_space.run(
        tmp_path / 'scores.xlsx', folder = data_folder, download = False,
        check = False)
    sheets = pd.read_excel(path, sheet_name = None)
    assert list(sheets) == ['Scores', 'About']
    scores = sheets['Scores']
    justices = scores.query('court_type == "Supreme Court"')
    assert justices['jcs'].isna().all()
    # Without the duty station, Judge Lutt has no state in the circuit, so
    # gets the president's score.
    lutt = scores.query('nid == 9').iloc[0]
    assert lutt['state_source'] == 'not found'
    assert lutt['jcs'] == pytest.approx(0.557)


def test_cli(data_folder, tmp_path) -> None:
    output = tmp_path / 'cli.xlsx'
    cli.main([
        '--output', str(output), '--data-folder', str(data_folder),
        '--no-download', '--senators', 'date', '--start-year', '1930'])
    scores = pd.read_excel(output, sheet_name = 'Scores')
    assert 7 in scores['nid'].tolist()
    green = scores.query('nid == 6').iloc[0]
    assert green['method'] == 'president'
    cli.main([
        '--output', str(output), '--data-folder', str(data_folder),
        '--no-download', '--use-published', '--published-threshold', '0.5'])
    scores = pd.read_excel(output, sheet_name = 'Scores')
    # Judge Poe's score differs from the published one by less than 0.5, as
    # does Chief Justice Smith's first term (by 0.43).
    assert scores.query('nid == 3').iloc[0]['jcs_source'] == 'computed'
    assert scores.query('nid == 5')['jcs_source'].tolist() == [
        'Epstein et al.', 'computed']


def test_cli_rejects_unknown_choices() -> None:
    with pytest.raises(SystemExit):
        cli.main(['--senators', 'year'])
