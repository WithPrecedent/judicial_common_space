"""Tests for finding where the judges of the courts of appeals sat."""

from __future__ import annotations

import json

import pandas as pd

from judicial_common_space import stations

FOURTH = """
== List of former judges ==
{{start U.S. judgeship Former}}
{{U.S. judgeship row Former
 | index        = 35
 | name         = {{sortname|J. Michael|Luttig}}
 | state        = [[Virginia|VA]]
 | borndied     = 1954–present
 | term         = 1991–2006
}}
{{U.S. judgeship row
 | index        = 2
 | name         = {{sortname|Simon|Sobeloff}}
 | state        = [[Maryland|MD]]
 | appointer    = Eisenhower<ref>{{cite web
  | title = A citation that spans lines
}}</ref>
 | term         = 1956–1970
}}
{{U.S. judgeship row Former
 | index        = 3
 | name         = {{sortname|Richard|Rives}}
 | state        = [[Alabama|AL]]
 | term         = —
}}
== Current composition of the court ==
{{U.S. judgeship row Current
 | name         = [[A. Marvin Quattlebaum Jr.]]
 | duty station = [[Greenville, South Carolina|Greenville, SC]]
 | term         = 2018–present
}}
{{U.S. judgeship row Current
 | name         = {{sortname|Somebody|Senior}}
 | duty station = ''inactive''
 | term         = 1990–2005
}}
"""


def test_parse() -> None:
    assert stations.parse(FOURTH) == [
        {'name': 'J. Michael Luttig', 'start': 1991, 'state': 'VA'},
        {'name': 'Simon Sobeloff', 'start': 1956, 'state': 'MD'},
        {'name': 'A. Marvin Quattlebaum Jr.', 'start': 2018, 'state': 'SC'}]


def test_duty_stations(tmp_path) -> None:
    path = tmp_path / 'stations.json'
    path.write_text(json.dumps({'pages': {
        '4': {'title': 'Fourth', 'revid': 1, 'wikitext': FOURTH}}}))
    table = stations.duty_stations(path)
    assert table['circuit'].tolist() == [4, 4, 4]
    assert table['state'].tolist() == ['VA', 'MD', 'SC']


def test_match() -> None:
    found = pd.DataFrame({
        'circuit': [4, 4, 9, 9, 9],
        'name': [
            'J. Michael Luttig', 'A. Marvin Quattlebaum Jr.', 'Milan Smith',
            'N. Randy Smith', "Diarmuid O'Scannlain"],
        'start': [1991, 2018, 2006, 2007, 1986],
        'state': ['VA', 'SC', 'CA', 'ID', 'OR']})

    def appointment(nid, last, circuit, commission, reassigned = False):
        return {
            'nid': nid, 'last_name': last, 'circuit': circuit,
            'court_type': 'U.S. Court of Appeals', 'court': f'Court {circuit}',
            'commission_date': commission, 'recess_date': '',
            'reassigned': reassigned}

    table = pd.DataFrame([
        appointment(1, 'Luttig', 4, '1991-08-02'),
        # The service began within a year of the commission.
        appointment(2, 'Quattlebaum', 4, '2019-01-02'),
        # Two judges Smith began within a year of 2006 in different states.
        appointment(3, 'Smith', 9, '2006-06-01'),
        appointment(4, "O'Scannlain", 9, '1986-11-10'),
        # Not the court that the row is on.
        appointment(5, 'Luttig', 9, '1991-08-02'),
        # Reassigned judges keep the state of the appointment before.
        appointment(6, 'Luttig', 4, '1991-08-02', reassigned = True)])
    assert stations.match(table, found) == {
        (1, 'Court 4'): 'VA', (2, 'Court 4'): 'SC', (4, 'Court 9'): 'OR'}
