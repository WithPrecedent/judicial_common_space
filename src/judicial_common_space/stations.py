"""Finds where the judges of the courts of appeals sat, from Wikipedia.

The Federal Judicial Center does not record the state that a judge of a
court of appeals came from or sat in. Wikipedia's article on each regional
court of appeals lists every judge who has served on it, each in a
"U.S. judgeship row" template whose "state" (for former judges) or "duty
station" (for sitting judges, as "Greenville, SC") names the judge's state:

```
{{U.S. judgeship row Former
 | index        = 35
 | name         = {{sortname|J. Michael|Luttig}}
 | state        = [[Virginia|VA]]
 | term         = 1991-2006
 ...
}}
```

`duty_stations` reads those rows from the file that `sources.download` saves,
and `match` finds the appointment of each one, so `states.home_state` can
fall back on it when a judge's career does not show a state. A judge whose
duty station is unknown (a senior judge listed as "inactive") has none.

Contents:
    duty_stations: returns the state of each judge in Wikipedia's articles.
    match: returns the Wikipedia state of each appointment to a court of
        appeals.
    parse: returns the judges in the source text of one article.

"""

from __future__ import annotations

import json
import pathlib
import re
import unicodedata

import pandas as pd

from . import options

_FIELD: re.Pattern[str] = re.compile(
    r'^\s*\|\s*(name|state|duty station|term)\s*=\s*(.*)$', re.MULTILINE)
_LINK: re.Pattern[str] = re.compile(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]')
_ROW: re.Pattern[str] = re.compile(
    r'\{\{U\.S\. judgeship row(?: Current| Former)?\s*\n')
_SORTNAME: re.Pattern[str] = re.compile(
    r'\{\{sortname\|([^|}]*)\|([^|}]*)')


def duty_stations(source: pathlib.Path | str) -> pd.DataFrame:
    """Returns the state of each judge in Wikipedia's articles.

    Args:
        source: the file that `sources.download` saves
            ("circuit_duty_stations.json").

    Returns:
        A table with "circuit", "name" (as the article gives it), "start"
            (the year the judge's service began), and "state" (a postal
            code), for every judge whose state is known.

    """
    saved = json.loads(pathlib.Path(source).read_text(encoding = 'utf-8'))
    rows = [
        {'circuit': int(number), **row}
        for number, page in saved['pages'].items()
        for row in parse(page['wikitext'])]
    return pd.DataFrame(rows, columns = ['circuit', 'name', 'start', 'state'])


def match(
    table: pd.DataFrame,
    stations: pd.DataFrame) -> dict[tuple[int, str], str]:
    """Returns the Wikipedia state of each appointment to a court of appeals.

    An appointment is the row of `stations` on the same court whose service
    began within a year of the appointment's commission (or recess
    appointment) and whose name contains every word of the judge's last
    name. If no row fits, or the rows that fit name different states, the
    appointment has none. A judge moved to a court without an appointment is
    not matched, since the judge keeps the home state of the appointment
    before.

    Args:
        table: the appointments (see `fjc.appointments`).
        stations: the judges' states (see `duty_stations`).

    Returns:
        The postal code of the state of each appointment that was matched,
            by the judge's "nid" and the court's name.

    """
    names = [set(_words(name)) for name in stations['name']]
    found = {}
    appeals = table[
        (table['court_type'] == 'U.S. Court of Appeals')
        & ~table['reassigned'].astype(bool)]
    for record in appeals.to_dict('records'):
        began = str(record['commission_date'] or record['recess_date'])[:4]
        last = set(_words(str(record['last_name'])))
        if not began.isdigit() or not last or pd.isna(record['circuit']):
            continue
        fits = {
            state for circuit, start, state, words in zip(
                stations['circuit'], stations['start'], stations['state'],
                names, strict = True)
            if circuit == record['circuit'] and abs(start - int(began)) <= 1
            and last <= words}
        if len(fits) == 1:
            found[(int(record['nid']), str(record['court']))] = fits.pop()
    return found


def parse(wikitext: str) -> list[dict[str, object]]:
    """Returns the judges in the source text of one article.

    Args:
        wikitext: the article's source text.

    Returns:
        The "name", "start" (the first year of the judge's service on the
            court), and "state" (a postal code) of each judge whose row
            gives all three. A row is read up to the start of the next one,
            so a footnote that spans lines does not cut it short.

    """
    starts = [found.end() for found in _ROW.finditer(wikitext)]
    rows = []
    for begin, end in zip(starts, [*starts[1:], len(wikitext)], strict = True):
        fields = dict(_FIELD.findall(wikitext[begin:end]))
        written = fields.get('name', '')
        sortname = _SORTNAME.search(written)
        name = (
            f'{sortname.group(1)} {sortname.group(2)}' if sortname
            else ' '.join(_LINK.findall(written)) or written)
        place = fields.get('state') or fields.get('duty station') or ''
        shown = ' '.join(_LINK.findall(place)) or place
        # "Greenville, SC" and "VA" both end with the state's postal code.
        state = shown.split(',')[-1].strip().replace('.', '').upper()
        start = re.search(r'\d{4}', fields.get('term', ''))
        if name.strip() and start and state in options._STATES:
            rows.append({
                'name': name.strip(), 'start': int(start.group()),
                'state': state})
    return rows


""" Private Functions """


def _words(text: str) -> list[str]:
    """Returns the words of a name, in lower case and without accents.

    Args:
        text: a name.

    Returns:
        Its words, without punctuation ("O'Scannlain" is "oscannlain").

    """
    plain = unicodedata.normalize('NFKD', text)
    plain = plain.encode('ascii', 'ignore').decode().lower()
    plain = plain.replace("'", '').replace('-', ' ')
    return re.sub(r'[^a-z ]', ' ', plain).split()
