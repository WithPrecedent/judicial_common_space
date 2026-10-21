"""Shared fixtures for the tests: small versions of every source file."""

from __future__ import annotations

import json
import pathlib

import pandas as pd
import pytest

from judicial_common_space import options, sources

SERVICE_COLUMNS = [
    'nid', 'Sequence', 'Judge Name', 'Court Type', 'Court Name',
    'Appointment Title', 'Appointing President',
    'Party of Appointing President', 'Reappointing President',
    'Party of Reappointing President', 'Recess Appointment Date',
    'Nomination Date', 'Confirmation Date', 'Commission Date',
    'Termination Date']
MD = 'U.S. District Court for the District of Maryland'
CO = 'U.S. District Court for the District of Colorado'
SCOTUS = 'Supreme Court of the United States'


def _service_row(nid, sequence, name, kind, court, president, party, **dates):
    return {
        'nid': str(nid), 'Sequence': str(sequence), 'Judge Name': name,
        'Court Type': kind, 'Court Name': court,
        'Appointment Title': dates.pop('title', 'Judge'),
        'Appointing President': president,
        'Party of Appointing President': party,
        'Reappointing President': dates.pop('reappointing', ''),
        'Party of Reappointing President': dates.pop('reappointing_party', ''),
        'Recess Appointment Date': dates.pop('recess', ''),
        'Nomination Date': dates.pop('nomination', ''),
        'Confirmation Date': dates.pop('confirmation', ''),
        'Commission Date': dates.pop('commission', ''),
        'Termination Date': dates.pop('termination', '')}


@pytest.fixture
def service() -> pd.DataFrame:
    """The federal judicial service of seven made-up judges."""
    rows = [
        _service_row(
            1, 1, 'Doe, Jane', 'U.S. District Court', MD, 'Barack Obama',
            'Democratic', nomination = '2011-02-01', commission = '2011-06-01',
            termination = '2014-06-01'),
        _service_row(
            1, 2, 'Doe, Jane', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the Fourth Circuit', 'Barack Obama',
            'Democratic', nomination = '2014-03-01',
            commission = '2014-06-02'),
        _service_row(
            2, 1, 'Roe, Richard', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the Fifth Circuit', 'Jimmy Carter',
            'Democratic', nomination = '1979-05-01', commission = '1979-09-01',
            termination = '1981-09-30'),
        _service_row(
            2, 2, 'Roe, Richard', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the Eleventh Circuit',
            'None (reassignment)', 'None (reassignment)',
            commission = '1981-10-01'),
        _service_row(
            3, 1, 'Poe, Edgar', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the District of Columbia Circuit',
            'Ronald Reagan', 'Republican', nomination = '1985-05-01',
            commission = '1985-08-01'),
        _service_row(
            4, 1, 'Hoe, Ann', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the Federal Circuit', 'Barack Obama',
            'Democratic', nomination = '2013-02-01',
            commission = '2013-05-01'),
        _service_row(
            5, 1, 'Smith, John', 'Supreme Court', SCOTUS, 'Richard M. Nixon',
            'Republican', title = 'Associate Justice',
            nomination = '1971-10-22', commission = '1972-01-07',
            termination = '1986-09-26'),
        _service_row(
            5, 2, 'Smith, John', 'Supreme Court', SCOTUS, 'Ronald Reagan',
            'Republican', title = 'Chief Justice', nomination = '1986-06-20',
            commission = '1986-09-26', termination = '2005-09-03'),
        _service_row(
            6, 1, 'Green, Gale', 'U.S. District Court', CO,
            'William J. Clinton', 'Democratic', nomination = '1995-03-31',
            commission = '1995-08-01'),
        _service_row(
            7, 1, 'Old, Otto', 'U.S. District Court', MD,
            'Franklin D. Roosevelt', 'Democratic', nomination = '1935-02-01',
            commission = '1935-05-01', termination = '1945-01-01'),
        _service_row(
            8, 1, 'Gray, Gil', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the Fourth Circuit',
            'William J. Clinton', 'Democratic', recess = '2000-12-27',
            nomination = '2001-05-09', commission = '2001-07-20',
            reappointing = 'George W. Bush',
            reappointing_party = 'Republican'),
        # Judge Lutt's career was in Washington, D.C., so only the duty
        # station shows the state.
        _service_row(
            9, 1, 'Lutt, Mike', 'U.S. Court of Appeals',
            'U.S. Court of Appeals for the Fourth Circuit',
            'George H.W. Bush', 'Republican', nomination = '1991-04-23',
            commission = '1991-08-02')]
    return pd.DataFrame(rows, columns = SERVICE_COLUMNS)


@pytest.fixture
def demographics() -> pd.DataFrame:
    """The demographics of the made-up judges."""
    people = [
        (1, 101, 'Doe', 'Jane', '', '', 'MD'),
        (2, 102, 'Roe', 'Richard', '', '', 'GA'),
        (3, 103, 'Poe', 'Edgar', '', '', 'VA'),
        (4, 104, 'Hoe', 'Ann', '', '', 'OH'),
        (5, 105, 'Smith', 'John', 'Paul', '', 'WI'),
        (6, 106, 'Green', 'Gale', '', '', 'CO'),
        (7, 107, 'Old', 'Otto', '', '', 'MD'),
        (8, 108, 'Gray', 'Gil', '', '', 'NY'),
        (9, 109, 'Lutt', 'Mike', '', '', 'TX')]
    return pd.DataFrame(
        [[str(cell) for cell in person] for person in people],
        columns = [
            'nid', 'jid', 'Last Name', 'First Name', 'Middle Name', 'Suffix',
            'Birth State'])


@pytest.fixture
def career() -> pd.DataFrame:
    """The careers of the made-up judges."""
    entries = [
        (2, 'Law clerk, Hon. Somebody, U.S. Court of Appeals for the Fifth '
            'Circuit, 1958-1959'),
        (2, 'Private practice, Atlanta, Georgia, 1960-1979'),
        (2, 'Visiting professor, Tulane Law School, 1975'),
        (3, 'Private practice, Washington, D.C., 1970-1985'),
        (8, 'Private practice, Richmond, Virginia, 1980-2000'),
        (8, 'Adjunct professor, Georgetown University Law Center, 1995-'),
        (9, 'Assistant counsel, White House, 1981-1982'),
        (9, 'Office of Legal Counsel, U.S. Department of Justice, 1989-1991')]
    return pd.DataFrame(
        [(str(nid), str(number), text)
         for number, (nid, text) in enumerate(entries, start = 1)],
        columns = ['nid', 'Sequence', 'Professional Career'])


def _member(congress, chamber, icpsr, state, party, name, bioguide, score):
    return {
        'congress': congress, 'chamber': chamber, 'icpsr': icpsr,
        'state_abbrev': state, 'party_code': party, 'bioname': name,
        'bioguide_id': bioguide, 'nominate_dim1': score}


@pytest.fixture
def members() -> pd.DataFrame:
    """Voteview's rows for the senators and presidents of the judges."""
    rows = []
    for congress in (112, 113):
        rows += [
            _member(congress, 'Senate', 1, 'MD', 100, 'MIKULSKI, Barbara',
                    'M000702', -0.4),
            _member(congress, 'Senate', 2, 'MD', 100, 'CARDIN, Ben',
                    'C000141', -0.3),
            _member(congress, 'President', 99911, 'USA', 100, 'OBAMA, Barack',
                    None, -0.358)]
    rows += [
        _member(96, 'Senate', 3, 'GA', 100, 'TALMADGE, Herman', 'T000022',
                -0.1),
        _member(96, 'Senate', 4, 'GA', 100, 'NUNN, Sam', 'N000171', -0.05),
        _member(96, 'President', 99906, 'USA', 100, 'CARTER, Jimmy', None,
                -0.504),
        _member(99, 'President', 99907, 'USA', 200, 'REAGAN, Ronald', None,
                0.692),
        _member(92, 'President', 99904, 'USA', 200, 'NIXON, Richard', None,
                0.552),
        # Ben Nighthorse Campbell changed parties on March 3, 1995, so he
        # has a row for each party in the 104th Congress.
        _member(104, 'Senate', 5, 'CO', 200, 'BROWN, Hank', 'B000918', 0.4),
        _member(104, 'Senate', 6, 'CO', 100, 'CAMPBELL, Ben', 'C000077',
                -0.14),
        _member(104, 'Senate', 7, 'CO', 200, 'CAMPBELL, Ben', 'C000077', 0.2),
        _member(104, 'President', 99909, 'USA', 100, 'CLINTON, Bill', None,
                -0.438),
        _member(102, 'Senate', 8, 'VA', 200, 'WARNER, John', 'W000154', 0.3),
        _member(102, 'Senate', 10, 'VA', 100, 'ROBB, Charles', 'R000309',
                -0.1),
        _member(102, 'President', 99908, 'USA', 200, 'BUSH, George H. W.',
                None, 0.557),
        _member(107, 'Senate', 8, 'VA', 200, 'WARNER, John', 'W000154', 0.3),
        _member(107, 'Senate', 9, 'VA', 200, 'ALLEN, George', 'A000121', 0.4),
        _member(107, 'President', 99910, 'USA', 200, 'BUSH, George W.', None,
                0.693)]
    return pd.DataFrame(rows)


@pytest.fixture
def legislators() -> list[dict[str, object]]:
    """The dates that the made-up judges' senators served."""

    def senator(bioguide, state, start, end, party, affiliations = None):
        term = {
            'type': 'sen', 'state': state, 'start': start, 'end': end,
            'party': party}
        if affiliations:
            term['party_affiliations'] = affiliations
        return {'id': {'bioguide': bioguide}, 'terms': [term]}

    return [
        senator('M000702', 'MD', '1987-01-06', '2017-01-03', 'Democrat'),
        senator('C000141', 'MD', '2007-01-04', '2025-01-03', 'Democrat'),
        senator('T000022', 'GA', '1957-01-03', '1981-01-03', 'Democrat'),
        senator('N000171', 'GA', '1972-11-08', '1997-01-03', 'Democrat'),
        senator('B000918', 'CO', '1991-01-03', '1997-01-03', 'Republican'),
        senator(
            'C000077', 'CO', '1993-01-05', '1999-01-03', 'Republican',
            [{'start': '1993-01-05', 'end': '1995-03-03',
              'party': 'Democrat'},
             {'start': '1995-03-03', 'end': '1999-01-03',
              'party': 'Republican'}]),
        senator('W000154', 'VA', '1979-01-02', '2009-01-03', 'Republican'),
        senator('R000309', 'VA', '1989-01-03', '2001-01-03', 'Democrat'),
        senator('A000121', 'VA', '2001-01-03', '2007-01-03', 'Republican')]


@pytest.fixture
def martin_quinn() -> pd.DataFrame:
    """Martin-Quinn scores of the made-up justice in a few terms."""
    terms = [1971, 1972, 1985, 1986, 1987]
    return pd.DataFrame({
        'term': terms,
        'justice': [100] * len(terms),
        'justiceName': ['JPSmith'] * len(terms),
        'post_mn': [3.0, 3.2, 3.5, 1.0, 1.2],
        'post_sd': [0.3] * len(terms)})


@pytest.fixture
def data_folder(
    tmp_path: pathlib.Path,
    service: pd.DataFrame,
    demographics: pd.DataFrame,
    career: pd.DataFrame,
    members: pd.DataFrame,
    legislators: list[dict[str, object]],
    martin_quinn: pd.DataFrame) -> pathlib.Path:
    """A data folder with every file, as `sources.paths` lays them out."""
    folder = tmp_path / 'data'
    found = sources.paths(folder)
    for path in found.values():
        path.parent.mkdir(parents = True, exist_ok = True)
    service.to_csv(found['service'], index = False)
    demographics.to_csv(found['demographics'], index = False)
    career.to_csv(found['career'], index = False)
    members.to_csv(found['congress'], index = False)
    found['legislators_historical'].write_text(
        json.dumps(legislators), encoding = 'utf-8')
    found['legislators_current'].write_text('[]', encoding = 'utf-8')
    martin_quinn.to_csv(found['martin_quinn'], index = False)
    found['duty_stations'].write_text(json.dumps({'pages': {'4': {
        'title': 'United States Court of Appeals for the Fourth Circuit',
        'revid': 1,
        'wikitext': (
            '{{U.S. judgeship row Former\n'
            ' | name         = {{sortname|Mike|Lutt}}\n'
            ' | state        = [[Virginia|VA]]\n'
            ' | term         = 1991–2006\n'
            '}}\n')}}}), encoding = 'utf-8')
    pd.DataFrame({
        'name': ['Doe, Jane', 'Roe, Richard', 'Roe, Richard', 'Poe, Edgar'],
        'circuit': [4, 5, 11, 12],
        'jcs': [-0.35, -0.075, -0.075, 0.5]}).to_csv(
            found['jcs_judges'], index = False)
    pd.DataFrame({
        'term': [1971, 1986], 'justiceName': ['JPSmith', 'JPSmith'],
        'jcs': [0.0, 0.0]}).to_csv(found['jcs_justices'], index = False)
    pd.DataFrame({
        'nid': [1, 6], 'judgename': ['Doe, Jane', 'Green, Gale'],
        'district1': ['DMD', 'DCO'], 'ideology_score': [-0.35, -0.438]}).to_csv(
            found['boyd'], index = False)
    return folder


@pytest.fixture(autouse = True)
def private_data(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch) -> None:
    """Keeps tests away from the user's real data folder."""
    monkeypatch.setenv(options._ENV_DATA, str(tmp_path / 'default'))
