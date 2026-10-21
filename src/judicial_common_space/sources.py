"""Downloads the files that the scores are computed from and checked against.

| Kind | File | Folder | Source |
| --- | --- | --- | --- |
| `service`, `demographics`, `career` | The Federal Judicial Center's files of judges' service on each court, their demographics (with both of the center's numbers for each judge, "nid" and "jid"), and their careers before the bench. | "judges" | https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export |
| `congress` | "HSall_members.csv": the DW-NOMINATE scores of every member of every Congress and of every president. | "politics" | https://voteview.com/data |
| `legislators_historical`, `legislators_current` | The dates that every senator served, with the senator's party on each day. | "politics" | https://github.com/unitedstates/congress-legislators |
| `martin_quinn` | "justices.csv": each justice's Martin-Quinn score in each term. | "politics" | https://mqscores.wustl.edu/measures.php |
| `duty_stations` | "circuit_duty_stations.json": the source text of Wikipedia's article on each regional court of appeals, which lists every judge with the judge's state or duty station (see `stations`). | "judges" | https://en.wikipedia.org (through its API) |
| `jcs_judges`, `jcs_justices`, `jcs_medians` | The published Judicial Common Space scores of the judges of the courts of appeals and the justices, and the medians of each year. | "jcs" | https://epstein.wustl.edu/jcs |
| `boyd` | Christina Boyd's scores of district judges, made in the same way. | "jcs" | https://sites.wustl.edu/clboyd/research |

The folders are in `utilities.data_folder()` and are the ones that courtpy
uses for the same files, so the projects share their downloads. The
Martin-Quinn page is behind a check for automated browsers, which can refuse
the download. Then save "justices.csv" from the page in a browser, and put it
in the "politics" folder (or pass its path).

Contents:
    download: downloads the files that are missing.
    paths: returns where each file is kept.
    _FOLDERS: the folder of each kind of file.
    _NAMES: the name of each kind of file.

"""

from __future__ import annotations

import json
import logging
import pathlib
import re
import zipfile
from collections.abc import Sequence
from typing import Any

from . import options, utilities

logger = logging.getLogger(__name__)

_NAMES: dict[str, str] = {
    **options._FJC_FILES,
    'congress': options._VOTEVIEW_FILE,
    **options._LEGISLATORS_FILES,
    'martin_quinn': options._MQ_FILE,
    'duty_stations': options._WIKIPEDIA_FILE,
    'jcs_judges': 'judges.csv',
    'jcs_justices': 'justices.csv',
    'jcs_medians': 'medians.csv',
    'boyd': 'boyd_district_judges.csv'}
_FOLDERS: dict[str, str] = {
    **dict.fromkeys([*options._FJC_FILES, 'duty_stations'], 'judges'),
    **dict.fromkeys(
        ['congress', *options._LEGISLATORS_FILES, 'martin_quinn'],
        'politics'),
    **dict.fromkeys(
        ['jcs_judges', 'jcs_justices', 'jcs_medians', 'boyd'], 'jcs')}


def download(
    kinds: Sequence[str] | str | None = None,
    folder: pathlib.Path | str | None = None,
    *,
    overwrite: bool = False,
    session: Any = None) -> dict[str, pathlib.Path]:
    """Downloads the files that are missing.

    Args:
        kinds: the files to download (see the module's documentation).
            Defaults to `None`, for all of them.
        folder: the data folder. Defaults to `None`, in which case
            `utilities.data_folder()` is used.
        overwrite: whether to download a file that is already there. The
            Federal Judicial Center adds judges as they are appointed, and
            Voteview changes the scores of sitting members as they vote.
            Defaults to `False`.
        session: an object with a `get` method like a `requests.Session`.
            Defaults to `None`, in which case a `requests.Session` is made.

    Raises:
        requests.HTTPError: if a page or a file cannot be downloaded.
        ValueError: if one of `kinds` is unknown, or a page has no link to
            its file.

    Returns:
        The path of each file, by its kind.

    """
    wanted = (
        list(_NAMES) if kinds is None
        else [kinds] if isinstance(kinds, str) else list(kinds))
    unknown = [kind for kind in wanted if kind not in _NAMES]
    if unknown:
        message = f'kinds must be among {list(_NAMES)}, not {unknown}'
        raise ValueError(message)
    found = paths(folder)
    session = utilities.open_session(session)
    archive_needed = False
    for kind in wanted:
        path = found[kind]
        if path.is_file() and not overwrite:
            continue
        if kind in options._FJC_FILES:
            utilities.download_file(
                options._FJC_URL + _NAMES[kind], path, overwrite = True,
                session = session)
        elif kind == 'congress':
            utilities.download_file(
                options._VOTEVIEW_URL + _NAMES[kind], path, overwrite = True,
                session = session)
        elif kind in options._LEGISLATORS_FILES:
            utilities.download_file(
                options._LEGISLATORS_URL + _NAMES[kind], path,
                overwrite = True, session = session)
        elif kind == 'martin_quinn':
            utilities.download_file(
                _link(options._MQ_PAGE, options._MQ_FILE, session), path,
                overwrite = True, session = session)
        elif kind == 'boyd':
            utilities.download_file(
                options._BOYD_URL, path, overwrite = True, session = session)
        elif kind == 'duty_stations':
            _download_wikipedia(path, session)
        else:
            archive_needed = True
    if archive_needed:
        _unpack_jcs(found, session)
    return {kind: found[kind] for kind in wanted}


def paths(folder: pathlib.Path | str | None = None) -> dict[str, pathlib.Path]:
    """Returns where each file is kept.

    Args:
        folder: the data folder. Defaults to `None`, in which case
            `utilities.data_folder()` is used.

    Returns:
        The path of each file, by its kind. The files need not exist.

    """
    base = (
        pathlib.Path(folder).expanduser() if folder
        else utilities.data_folder())
    return {kind: base / _FOLDERS[kind] / name for kind, name in _NAMES.items()}


""" Private Functions """


def _download_wikipedia(path: pathlib.Path, session: Any) -> None:
    """Saves the source text of Wikipedia's articles on the courts of appeals.

    Each article (see `options._WIKIPEDIA_PAGES`) is requested from
    Wikipedia's API, and all of them are saved in one JSON file with the
    number of the revision that was read, so the file shows which versions
    the duty stations came from.

    Args:
        path: where to save the file. Its folder is created if needed.
        session: an object with a `get` method like a `requests.Session`.

    Raises:
        requests.HTTPError: if an article cannot be downloaded.
        ValueError: if the API does not return an article.

    """
    pages = {}
    for number, title in options._WIKIPEDIA_PAGES.items():
        response = session.get(
            options._WIKIPEDIA_API,
            params = {
                'action': 'parse', 'page': title, 'prop': 'wikitext|revid',
                'redirects': 1, 'format': 'json', 'formatversion': 2},
            timeout = options._TIMEOUT)
        response.raise_for_status()
        parsed = json.loads(response.text).get('parse')
        if not parsed:
            message = f'Wikipedia returned no article titled {title!r}'
            raise ValueError(message)
        pages[str(number)] = {
            'title': parsed.get('title', title),
            'revid': parsed.get('revid'),
            'wikitext': parsed['wikitext']}
    path.parent.mkdir(parents = True, exist_ok = True)
    path.write_text(
        json.dumps({'source': options._WIKIPEDIA_API, 'pages': pages}),
        encoding = 'utf-8')
    logger.info('downloaded %d Wikipedia articles to %s', len(pages), path)


def _link(page: str, name: str, session: Any) -> str:
    """Returns the address of the link to a file on a page.

    Args:
        page: the address of the page.
        name: the name of the file, which the link ends with.
        session: an object with a `get` method like a `requests.Session`.

    Raises:
        requests.HTTPError: if the page cannot be downloaded.
        ValueError: if the page has no link to the file.

    Returns:
        The full address of the first link whose path ends with `name`.

    """
    for address, _ in utilities.page_links(page, session = session):
        if address.split('?', 1)[0].rsplit('/', 1)[-1].lower() == name.lower():
            return address
    message = (
        f'no link to {name!r} was found on {page}: download the file in a '
        f'browser and pass its path instead')
    raise ValueError(message)


def _unpack_jcs(found: dict[str, pathlib.Path], session: Any) -> None:
    """Downloads the archive of Judicial Common Space scores and unpacks it.

    The archive (about 100 kilobytes) is found by its link on
    `options._JCS_PAGE`, and is kept beside its CSV files.

    Args:
        found: the path of each kind of file (see `paths`).
        session: an object with a `get` method like a `requests.Session`.

    Raises:
        requests.HTTPError: if the page or the archive cannot be downloaded.
        ValueError: if the page has no link to an archive, or the archive
            lacks a file.

    """
    links = utilities.page_links(options._JCS_PAGE, session = session)
    addresses = [
        address for address, _ in links
        if address.lower().split('?', 1)[0].endswith('.zip')]
    if not addresses:
        message = f'no link to an archive was found on {options._JCS_PAGE}'
        raise ValueError(message)
    folder = found['jcs_judges'].parent
    archive = utilities.download_file(
        addresses[0], folder / addresses[0].rsplit('/', 1)[-1],
        overwrite = True, session = session)
    with zipfile.ZipFile(archive) as unpacked:
        # The archive was made on a Mac, so it has a "__MACOSX" folder of
        # hidden files with the same names.
        members = [
            name for name in unpacked.namelist()
            if name.lower().endswith('.csv') and '__MACOSX' not in name]
        for kind, pattern in options._JCS_FILES.items():
            matches = [
                name for name in members
                if re.search(pattern, name.rsplit('/', 1)[-1], re.IGNORECASE)]
            if not matches:
                message = f'the archive {archive} has no CSV file of {kind}'
                raise ValueError(message)
            found[f'jcs_{kind}'].write_bytes(unpacked.read(matches[0]))
    logger.info('unpacked the Judicial Common Space scores to %s', folder)
