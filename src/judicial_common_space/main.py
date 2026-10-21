"""Computes the scores, checks them, and writes the spreadsheet.

```python
import judicial_common_space

judicial_common_space.run('judicial_common_space.xlsx')
```

Contents:
    compute: returns the scores of the appointments and of the justices.
    run: downloads the files that are missing, computes and checks the
        scores, and writes the spreadsheet.
    _INPUTS: the kinds of files that the scores are computed from.
    _PUBLISHED: the kinds of files of published scores that they are
        checked against.

"""

from __future__ import annotations

import logging
import pathlib
from typing import Any

import pandas as pd

from . import export, fjc, options, politics, scores, sources, utilities, verify

logger = logging.getLogger(__name__)

_INPUTS: tuple[str, ...] = (
    'service', 'demographics', 'career', 'congress', 'legislators_historical',
    'legislators_current')
_PUBLISHED: tuple[str, ...] = ('jcs_judges', 'jcs_justices', 'boyd')


def compute(
    files: dict[str, pathlib.Path],
    *,
    senators: str = 'congress',
    martin_quinn: pathlib.Path | str | None = None,
    transformation: str = 'jcs2024') -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns the scores of the appointments and of the justices.

    Args:
        files: the path of each file, by its kind (see `sources.paths`).
        senators: which senators count, "congress" or "date" (see
            `politics.Senate.senators`). Defaults to "congress".
        martin_quinn: the file of the justices' Martin-Quinn scores.
            Defaults to `None`, in which case the one in the data folder is
            used if there is one.
        transformation: the transformation of Martin-Quinn scores, "jcs2024"
            or "paper" (see `politics.justices`). Defaults to "jcs2024".

    Returns:
        The scores of every appointment (see `scores.appointments`), and of
            every justice in every term (see `scores.justices`), which is
            empty if there are no Martin-Quinn scores.

    """
    table = fjc.appointments(files['service'], files['demographics'])
    careers = fjc.careers(files['career'])
    senate = politics.Senate.from_files(
        files['congress'],
        [files['legislators_historical'], files['legislators_current']])
    path = pathlib.Path(martin_quinn) if martin_quinn else files['martin_quinn']
    terms = pd.DataFrame()
    if path.is_file():
        terms = scores.justices(
            politics.justices(path, transformation), table, start_year = 0)
    else:
        logger.warning(
            'there are no Martin-Quinn scores at %s, so the justices have no '
            'scores: save "justices.csv" from %s there', path, options._MQ_PAGE)
    scored = scores.appointments(
        table, careers, senate, start_year = None, senators = senators,
        terms = terms)
    return scored, terms


def run(
    output: pathlib.Path | str = 'judicial_common_space.xlsx',
    *,
    folder: pathlib.Path | str | None = None,
    start_year: int = options._START_YEAR,
    senators: str = 'congress',
    martin_quinn: pathlib.Path | str | None = None,
    transformation: str = 'jcs2024',
    download: bool = True,
    overwrite: bool = False,
    check: bool = True,
    session: Any = None) -> pathlib.Path:
    """Downloads the files that are missing, computes and checks the scores.

    Then it writes the spreadsheet (see `export.write`).

    Args:
        output: where to save the spreadsheet. Defaults to
            "judicial_common_space.xlsx" in the current folder.
        folder: the data folder. Defaults to `None`, in which case
            `utilities.data_folder()` is used.
        start_year: the first year of service to include (see
            `scores.appointments`). Defaults to 1953, the first year of
            Epstein et al.'s study. The justices' terms begin with the one
            that was sitting in January of that year (the 1952 term, for
            1953), as the study's do.
        senators: which senators count, "congress" or "date" (see
            `politics.Senate.senators`). Defaults to "congress", as in the
            published Judicial Common Space scores.
        martin_quinn: the file of the justices' Martin-Quinn scores.
            Defaults to `None`, in which case the one in the data folder is
            used, which is downloaded if it can be.
        transformation: the transformation of Martin-Quinn scores, "jcs2024"
            (as in the 2024 release of the scores) or "paper" (Epstein et
            al.'s of 2007; see `politics.justices`). Defaults to "jcs2024".
        download: whether to download the files that are missing. Defaults
            to `True`.
        overwrite: whether to download the files again even if they are
            there. Defaults to `False`.
        check: whether to compare the scores with published scores.
            Defaults to `True`.
        session: an object with a `get` method like a `requests.Session`.
            Defaults to `None`, in which case a `requests.Session` is made.

    Returns:
        The path of the spreadsheet.

    """
    files = sources.paths(folder)
    if download:
        session = utilities.open_session(session)
        sources.download(
            _INPUTS, folder, overwrite = overwrite, session = session)
        optional = [] if martin_quinn else ['martin_quinn']
        optional += list(_PUBLISHED) if check else []
        for kind in optional:
            try:
                sources.download(
                    kind, folder, overwrite = overwrite, session = session)
            except Exception as error:  # noqa: BLE001
                logger.warning('could not download %s: %s', kind, error)
    scored, terms = compute(
        files, senators = senators, martin_quinn = martin_quinn,
        transformation = transformation)
    sheets: dict[str, pd.DataFrame] = {
        'Scores': _since(scored, start_year),
        # A term begins in October, so the one sitting in January of the
        # first year began the year before.
        'Justices': (
            terms[terms['term'] >= start_year - 1] if not terms.empty
            else terms)}
    if check:
        checks = _checks(files, scored, terms)
        sheets['Verification'] = verify.summarize(checks)
        names = {
            'circuit_judges': 'Circuit check',
            'district_judges': 'District check',
            'justices': 'Justice check'}
        sheets.update({names[name]: table for name, table in checks.items()})
        for row in sheets['Verification'].to_dict('records'):
            logger.info(
                '%s: %d of %d found; %.1f%% the same and %.1f%% the same or '
                'within %.2f', row['check'], row['found'], row['published'],
                100 * row['share_same'], 100 * row['share_same_or_close'],
                verify._CLOSE)
    settings = {
        'start_year': start_year, 'senators': senators,
        'transformation': transformation,
        'appointments': len(sheets['Scores'])}
    path = export.write(output, sheets, settings)
    missing = int(sheets['Scores']['jcs'].isna().sum())
    logger.info(
        'wrote %d appointments to %s (%d without a score)',
        len(sheets['Scores']), path, missing)
    return path


""" Private Functions """


def _checks(
    files: dict[str, pathlib.Path],
    scored: pd.DataFrame,
    terms: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Returns the comparisons with the published scores that are there.

    Args:
        files: the path of each file, by its kind (see `sources.paths`).
        scored: the scores of every appointment.
        terms: the scores of every justice in every term.

    Returns:
        The results of `verify.circuit_judges`, `verify.district_judges`,
            and `verify.justices`, by the name of each, for the published
            files that are there.

    """
    checks = {}
    if files['jcs_judges'].is_file():
        checks['circuit_judges'] = verify.circuit_judges(
            scored, utilities.read_csv(files['jcs_judges']))
    if files['boyd'].is_file():
        checks['district_judges'] = verify.district_judges(
            scored, utilities.read_csv(files['boyd']))
    if files['jcs_justices'].is_file() and not terms.empty:
        checks['justices'] = verify.justices(
            terms, utilities.read_csv(files['jcs_justices']))
    return checks


def _since(scored: pd.DataFrame, start_year: int) -> pd.DataFrame:
    """Returns the appointments of judges who served in or after a year.

    Args:
        scored: the scores of every appointment.
        start_year: the year.

    Returns:
        The appointments whose service ended in or after `start_year`, or
            has not ended.

    """
    first = f'{start_year}-01-01'
    serving = (scored['termination_date'] == '') | (
        scored['termination_date'] >= first)
    return scored[serving].reset_index(drop = True)
