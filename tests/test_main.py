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
    summary = sheets['Verification'].set_index('check')
    assert summary.loc['circuit_judges', 'found'] == 4
    assert summary.loc['circuit_judges', 'same'] == 3
    assert summary.loc['district_judges', 'same'] == 1
    assert 'senators: congress' in sheets['About']['About'].tolist()


def test_run_starts_with_the_term_sitting_in_january(
    data_folder,
    tmp_path) -> None:
    path = judicial_common_space.run(
        tmp_path / 'scores.xlsx', folder = data_folder, download = False,
        start_year = 1973, check = False)
    justices = pd.read_excel(path, sheet_name = 'Justices')
    # The 1972 term was sitting in January 1973; the 1971 term was not.
    assert justices['term'].tolist() == [1972, 1985, 1986, 1987]


def test_run_without_martin_quinn(data_folder, tmp_path) -> None:
    sources.paths(data_folder)['martin_quinn'].unlink()
    path = judicial_common_space.run(
        tmp_path / 'scores.xlsx', folder = data_folder, download = False,
        check = False)
    sheets = pd.read_excel(path, sheet_name = None)
    assert list(sheets) == ['Scores', 'About']
    justices = sheets['Scores'].query('court_type == "Supreme Court"')
    assert justices['jcs'].isna().all()


def test_cli(data_folder, tmp_path) -> None:
    output = tmp_path / 'cli.xlsx'
    cli.main([
        '--output', str(output), '--data-folder', str(data_folder),
        '--no-download', '--senators', 'date', '--start-year', '1930'])
    scores = pd.read_excel(output, sheet_name = 'Scores')
    assert 7 in scores['nid'].tolist()
    green = scores.query('nid == 6').iloc[0]
    assert green['method'] == 'president'


def test_cli_rejects_unknown_choices() -> None:
    with pytest.raises(SystemExit):
        cli.main(['--senators', 'year'])
