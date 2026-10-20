"""Command line interface for computing Judicial Common Space scores.

Examples:
    python -m judicial_common_space
    judicial-common-space --output scores.xlsx --start-year 1980
    judicial-common-space --senators date --martin-quinn justices.csv

"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence

from . import main as jcs
from . import options


def main(arguments: Sequence[str] | None = None) -> None:
    """Computes the scores as the command line arguments say.

    Args:
        arguments: The command line arguments. Defaults to None, in which case
            the arguments passed to the program are used.

    """
    parsed = _get_parser().parse_args(arguments)
    logging.basicConfig(level = logging.INFO, format = '%(message)s')
    jcs.run(
        parsed.output,
        folder = parsed.data_folder,
        start_year = parsed.start_year,
        senators = parsed.senators,
        martin_quinn = parsed.martin_quinn,
        transformation = parsed.transformation,
        download = not parsed.no_download,
        overwrite = parsed.overwrite,
        check = not parsed.no_check)


def _get_parser() -> argparse.ArgumentParser:
    """Returns the parser for the command line arguments.

    Returns:
        argparse.ArgumentParser: The command line parser.

    """
    parser = argparse.ArgumentParser(
        prog = 'judicial-common-space',
        description = (
            'Compute the Judicial Common Space score of every appointment of '
            'a federal judge, check them against published scores, and save '
            'them in a spreadsheet.'))
    parser.add_argument(
        '--output',
        default = 'judicial_common_space.xlsx',
        help = 'where to save the spreadsheet (default: %(default)s)')
    parser.add_argument(
        '--start-year',
        type = int,
        default = options._START_YEAR,
        help = (
            'include judges who served on a court in this year or later '
            '(default: %(default)s)'))
    parser.add_argument(
        '--senators',
        choices = ['congress', 'date'],
        default = 'congress',
        help = (
            "count every senator of the president's party who sat in the "
            'Congress of the nomination, as the published scores do '
            '("congress"), or only those who held the seats on the day '
            '("date") (default: %(default)s)'))
    parser.add_argument(
        '--martin-quinn',
        default = None,
        help = (
            'the Martin-Quinn "justices.csv" file, if it cannot be '
            'downloaded (default: the one in the data folder)'))
    parser.add_argument(
        '--transformation',
        choices = list(options._ARCTANGENT),
        default = 'jcs2024',
        help = (
            'put Martin-Quinn scores on the scale as the 2024 release of the '
            'scores does ("jcs2024") or with the coefficients of the 2007 '
            'article ("paper") (default: %(default)s)'))
    parser.add_argument(
        '--data-folder',
        default = None,
        help = (
            'the folder for the downloaded files (default: "data/courts" '
            'beside the folder of code projects, as for courtpy)'))
    parser.add_argument(
        '--overwrite',
        action = 'store_true',
        help = (
            'download the files again, as when the Federal Judicial Center '
            'has added judges or Voteview has added votes'))
    parser.add_argument(
        '--no-download',
        action = 'store_true',
        help = 'use only the files that are already in the data folder')
    parser.add_argument(
        '--no-check',
        action = 'store_true',
        help = 'do not compare the scores with published scores')
    return parser


if __name__ == '__main__':
    main()
