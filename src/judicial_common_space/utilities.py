"""Shared tools, adapted from courtpy's.

Contents:
    data_folder: returns the folder for downloads.
    download_file: downloads a file, unless it was downloaded before.
    normalize: collapses all whitespace in text into single spaces.
    open_session: returns a session that identifies judicial_common_space to
        servers.
    page_links: returns the links on a web page.
    read_csv: loads a CSV file that is in UTF-8 or Windows-1252.
    logger: the module's logger, which reports the files that are downloaded.

"""

from __future__ import annotations

import html.parser
import logging
import os
import pathlib
import sys
import urllib.parse
from typing import Any

import pandas as pd
import requests

from . import options

logger = logging.getLogger(__name__)


class _LinkExtractor(html.parser.HTMLParser):
    """Collects the links of a web page, with the words of each.

    `html.parser.HTMLParser` reads the markup and calls the `handle_...`
    methods for each tag and piece of text, which this class records. Feed it
    markup with `feed`, call `close`, and read `links`.

    Attributes:
        links: the address ("href") and the words of each link found so far,
            in the order of the page. The words are a `list` of the pieces
            of text in the link.
        open: whether the parser is inside a link, so that text belongs to
            the last of `links`.

    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs = True)
        self.links: list[tuple[str, list[str]]] = []
        self.open: bool = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]]) -> None:
        """Starts a link at an "a" tag that has an address.

        Args:
            tag: name of the tag, in lower case.
            attrs: the tag's attributes, as pairs of names and values.

        """
        if tag == 'a':
            address = dict(attrs).get('href')
            self.open = bool(address)
            if address:
                self.links.append((address, []))

    def handle_endtag(self, tag: str) -> None:
        """Ends a link at the closing "a" tag.

        Args:
            tag: name of the tag, in lower case.

        """
        if tag == 'a':
            self.open = False

    def handle_data(self, data: str) -> None:
        """Records text that is inside a link.

        Args:
            data: text between tags.

        """
        if self.open:
            self.links[-1][1].append(data)


def data_folder() -> pathlib.Path:
    """Returns the folder for downloads.

    The folder is the one named by the `JUDICIAL_COMMON_SPACE_DATA_DIR`
    environment variable, if it is set. Otherwise, when judicial_common_space
    runs from its repository, it is `options._DATA_FOLDER`: "data/courts" two
    folders above the repository, beside the folder of code projects (where
    courtpy and fjc-idb keep their files as well). When it is installed as a
    package, it is "judicial_common_space" in the user's local application
    data folder on Windows ("%LOCALAPPDATA%"), or in "~/.local/share" (or
    "$XDG_DATA_HOME") on other systems.

    Returns:
        The path of the folder. It is not created.

    """
    named = os.environ.get(options._ENV_DATA)
    if named:
        return pathlib.Path(named).expanduser()
    if (pathlib.Path(__file__).parents[2] / 'pyproject.toml').is_file():
        return options._DATA_FOLDER
    if sys.platform == 'win32':
        base = (
            os.environ.get('LOCALAPPDATA')
            or pathlib.Path.home() / 'AppData' / 'Local')
        return pathlib.Path(base) / 'judicial_common_space'
    base = (
        os.environ.get('XDG_DATA_HOME')
        or pathlib.Path.home() / '.local' / 'share')
    return pathlib.Path(base) / 'judicial_common_space'


def download_file(
    url: str,
    path: pathlib.Path | str,
    *,
    overwrite: bool = False,
    session: Any = None) -> pathlib.Path:
    """Downloads a file, unless it was downloaded before.

    Args:
        url: the address of the file.
        path: where to save it. Its folder is created if needed.
        overwrite: whether to download the file even if there is one at
            `path`. Defaults to `False`.
        session: an object with a `get` method like a `requests.Session`.
            Defaults to `None`, in which case a `requests.Session` that
            identifies judicial_common_space is made.

    Raises:
        requests.HTTPError: if the file cannot be downloaded.

    Returns:
        `path`.

    """
    path = pathlib.Path(path)
    if overwrite or not path.is_file():
        response = open_session(session).get(url, timeout = options._TIMEOUT)
        response.raise_for_status()
        path.parent.mkdir(parents = True, exist_ok = True)
        path.write_bytes(response.content)
        logger.info('downloaded %s to %s', path.name, path.parent)
    return path


def normalize(text: str | None) -> str:
    """Collapses all whitespace in `text` into single spaces.

    Args:
        text: text to normalize. `None` becomes an empty `str`.

    Returns:
        The text on one line, with single spaces between words.

    """
    return ' '.join(text.split()) if text else ''


def open_session(session: Any = None) -> Any:
    """Returns a session that identifies judicial_common_space to servers.

    Args:
        session: an object with a `get` method like a `requests.Session`.
            Defaults to `None`.

    Returns:
        `session`, or a new `requests.Session` with judicial_common_space's
            user agent if it is `None`.

    """
    if session is None:
        session = requests.Session()
        session.headers.update({'User-Agent': options._USER_AGENT})
    return session


def page_links(url: str, *, session: Any = None) -> list[tuple[str, str]]:
    """Returns the links on a web page.

    Args:
        url: the address of the page.
        session: an object with a `get` method like a `requests.Session`.
            Defaults to `None`, in which case a `requests.Session` that
            identifies judicial_common_space is made.

    Raises:
        requests.HTTPError: if the page cannot be downloaded.

    Returns:
        The full address and the words of each link, in the order of the
            page. The words are on one line, with single spaces.

    """
    response = open_session(session).get(url, timeout = options._TIMEOUT)
    response.raise_for_status()
    extractor = _LinkExtractor()
    extractor.feed(response.text)
    extractor.close()
    return [
        (urllib.parse.urljoin(url, address), normalize(' '.join(words)))
        for address, words in extractor.links]


def read_csv(path: pathlib.Path | str, **kwargs: Any) -> pd.DataFrame:
    """Loads a CSV file that is in UTF-8 or Windows-1252.

    The files of other researchers' data are not all in UTF-8 (the Judicial
    Common Space files are in Windows-1252).

    Args:
        path: the path of the file, which may begin with "~" for the user's
            home folder.
        **kwargs: arguments for `pandas.read_csv`.

    Returns:
        The table.

    """
    path = pathlib.Path(path).expanduser()
    table: pd.DataFrame
    try:
        table = pd.read_csv(path, encoding = 'utf-8-sig', **kwargs)
    except UnicodeDecodeError:
        table = pd.read_csv(path, encoding = 'cp1252', **kwargs)
    return table
