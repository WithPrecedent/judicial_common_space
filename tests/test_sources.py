"""Tests for downloading the source files."""

from __future__ import annotations

import io
import json
import zipfile

import pytest

from judicial_common_space import options, sources, utilities


class FakeResponse:
    """A response of the fake web."""

    def __init__(self, content: bytes) -> None:
        self.content = content
        self.text = content.decode('utf-8', 'ignore')

    def raise_for_status(self) -> None:
        """Does nothing: every request of the fake web succeeds."""


class FakeSession:
    """Answers requests with fixed pages and files, and records them."""

    def __init__(self, pages: dict[str, bytes]) -> None:
        self.pages = pages
        self.requested: list[str] = []

    def get(
        self,
        url: str,
        params: dict[str, object] | None = None,
        timeout: int = 0) -> FakeResponse:
        """Returns the page or file at `url`, or the address itself.

        A request of Wikipedia's API returns an article whose source text is
        its title.

        """
        self.requested.append(url)
        if url == options._WIKIPEDIA_API and params:
            article = {
                'title': params['page'], 'revid': 7,
                'wikitext': f"text of {params['page']}"}
            return FakeResponse(json.dumps({'parse': article}).encode())
        return FakeResponse(self.pages.get(url, url.encode()))


def _archive() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as archive:
        archive.writestr('jcs 2024/csv/coa_judges_2024.csv', 'name,jcs\n')
        archive.writestr('__MACOSX/jcs 2024/csv/._coa_judges_2024.csv', 'x')
        archive.writestr(
            'jcs 2024/csv/jcs_supreme_court_2024_long.csv', 'term,jcs\n')
        archive.writestr(
            'jcs 2024/csv/jcs_supreme_court_2024_wide.csv', 'wide\n')
        archive.writestr('jcs 2024/csv/jcs medians.csv', 'year\n')
    return buffer.getvalue()


@pytest.fixture
def session() -> FakeSession:
    return FakeSession({
        options._MQ_PAGE: b'<a href="/media/2024/justices.csv">Justices</a>',
        options._JCS_PAGE: b'<a href="/s/JCS2024.zip">data</a>',
        'https://epstein.wustl.edu/s/JCS2024.zip': _archive()})


def test_paths(tmp_path) -> None:
    found = sources.paths(tmp_path)
    assert found['service'] == (
        tmp_path / 'judges' / 'federal-judicial-service.csv')
    assert found['congress'] == tmp_path / 'politics' / 'HSall_members.csv'
    assert found['martin_quinn'] == tmp_path / 'politics' / 'justices.csv'
    assert found['jcs_judges'] == tmp_path / 'jcs' / 'judges.csv'


def test_paths_default_to_the_data_folder() -> None:
    assert sources.paths()['boyd'].parent == utilities.data_folder() / 'jcs'


def test_download(session, tmp_path) -> None:
    found = sources.download(folder = tmp_path, session = session)
    assert set(found) == set(sources._NAMES)
    assert found['service'].read_text() == (
        options._FJC_URL + 'federal-judicial-service.csv')
    assert found['martin_quinn'].read_text() == (
        'https://mqscores.wustl.edu/media/2024/justices.csv')
    assert found['jcs_judges'].read_text() == 'name,jcs\n'
    assert found['jcs_justices'].read_text() == 'term,jcs\n'
    assert found['jcs_medians'].read_text() == 'year\n'
    saved = json.loads(found['duty_stations'].read_text(encoding = 'utf-8'))
    assert sorted(saved['pages'], key = int) == [str(n) for n in range(1, 12)]
    fourth = saved['pages']['4']
    assert fourth['title'] == (
        'United States Court of Appeals for the Fourth Circuit')
    assert fourth['revid'] == 7
    assert fourth['wikitext'] == f"text of {fourth['title']}"
    # Files that are there are not downloaded again.
    session.requested.clear()
    sources.download('congress', tmp_path, session = session)
    assert session.requested == []
    sources.download('congress', tmp_path, overwrite = True, session = session)
    assert session.requested == [
        options._VOTEVIEW_URL + options._VOTEVIEW_FILE]


def test_download_errors(session, tmp_path) -> None:
    with pytest.raises(ValueError, match = 'kinds must be among'):
        sources.download('unknown', tmp_path, session = session)
    session.pages[options._MQ_PAGE] = b'<p>No links</p>'
    with pytest.raises(ValueError, match = 'download the file in a browser'):
        sources.download('martin_quinn', tmp_path, session = session)

    def missing(url, params = None, timeout = 0):
        return FakeResponse(b'{"error": {"code": "missingtitle"}}')

    session.get = missing
    with pytest.raises(ValueError, match = 'no article titled'):
        sources.download('duty_stations', tmp_path, session = session)
