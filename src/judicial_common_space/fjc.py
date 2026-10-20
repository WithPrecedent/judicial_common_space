"""Reads the Federal Judicial Center's Biographical Directory of judges.

The directory's files that are organized by category (see `sources`) have a
row for each court that each judge served on ("federal-judicial-service.csv"),
for each judge ("demographics.csv"), and for each position that a judge held
before (and after) joining the bench ("professional-career.csv").

`appointments` makes a table with a row for each court that each judge served
on, which is one appointment unless the judge was moved to the court without
one (as the judges of the Fifth Circuit who were reassigned to the Eleventh
in 1981 were): such a row is marked `reassigned` and keeps the president,
party, and dates of the judge's appointment before. Most of this is borrowed
from `courtpy.judges.build_roster`.

Contents:
    appointments: returns a row for each court that each judge served on.
    careers: returns the entries of each judge's career, in the file's order.
    _COLUMNS: the columns of `appointments`, by their names in the file of
        service.
    _INHERITED: the columns that a reassigned judge's row takes from the
        judge's row before.
    _ORDINALS: the number of each court of appeals, by the words of its name.

"""

from __future__ import annotations

import pathlib

import pandas as pd

from . import utilities

_COLUMNS: dict[str, str] = {
    'Judge Name': 'judge',
    'Court Type': 'court_type',
    'Court Name': 'court',
    'Appointment Title': 'title',
    'Recess Appointment Date': 'recess_date',
    'Nomination Date': 'nomination_date',
    'Confirmation Date': 'confirmation_date',
    'Commission Date': 'commission_date',
    'Termination Date': 'termination_date'}
_INHERITED: tuple[str, ...] = (
    'president', 'party', 'recess_date', 'nomination_date',
    'confirmation_date', 'commission_date')
_ORDINALS: dict[str, int] = {
    'First': 1, 'Second': 2, 'Third': 3, 'Fourth': 4, 'Fifth': 5,
    'Sixth': 6, 'Seventh': 7, 'Eighth': 8, 'Ninth': 9, 'Tenth': 10,
    'Eleventh': 11, 'District of Columbia': 12, 'Federal': 13}


def appointments(
    service: pd.DataFrame | pathlib.Path | str,
    demographics: pd.DataFrame | pathlib.Path | str) -> pd.DataFrame:
    """Returns a row for each court that each judge served on.

    | Column | Meaning |
    | --- | --- |
    | `nid`, `jid` | The Federal Judicial Center's two numbers for the judge. |
    | `judge` | The judge's name, as the center reports it ("Last, First Middle"). |
    | `last_name`, `first_name`, `middle_name`, `suffix` | Its parts. |
    | `sequence` | The order of the judge's service on this court among the judge's courts. |
    | `court_type`, `court`, `title` | The court's type and name, and the judge's title on it. |
    | `circuit` | The number of a court of appeals (12 for the District of Columbia Circuit and 13 for the Federal Circuit). Missing for other courts. |
    | `president`, `party` | The president who appointed the judge and that president's party. A judge whose recess appointment was confirmed after a new president nominated the judge again (as Roger Gregory was) has the president who nominated the judge to the Senate. |
    | `recess_date`, `nomination_date`, `confirmation_date`, `commission_date`, `termination_date` | The dates of the appointment and of the end of the service, as YYYY-MM-DD. Blank if there was none. |
    | `appointment_date` | The date that the judge's senators and president are found on: the nomination, or the recess appointment, confirmation, or commission if there was no nomination. |
    | `reassigned` | Whether the judge was moved to the court without an appointment, in which case the judge has the president and dates of the appointment before. |
    | `earlier` | The courts that the judge served on before, as a tuple of their names. |
    | `birth_state` | The postal code of the state where the judge was born. |

    Args:
        service: the file of federal judicial service, as a path or a table.
        demographics: the file of demographics, as a path or a table.

    Raises:
        KeyError: if a file lacks a column that is needed.

    Returns:
        The table, sorted by the judges' numbers and then by the order of
            each judge's service.

    """
    served = _read(service)
    people = _read(demographics)
    _require(
        served,
        ['nid', 'Sequence', 'Appointing President',
         'Party of Appointing President', *_COLUMNS],
        'the file of federal judicial service')
    _require(
        people,
        ['nid', 'jid', 'Last Name', 'First Name', 'Middle Name', 'Suffix',
         'Birth State'],
        'the file of demographics')
    served = served.assign(
        nid = served['nid'].astype(int),
        sequence = pd.to_numeric(served['Sequence'], errors = 'coerce'))
    served = served.sort_values(['nid', 'sequence'], kind = 'stable')
    served = served.reset_index(drop = True)
    table = served[list(_COLUMNS)].rename(columns = _COLUMNS)
    table.insert(0, 'nid', served['nid'])
    table.insert(1, 'sequence', served['sequence'].astype('Int64'))
    # A judge who was renominated by a new president after a recess
    # appointment was confirmed on that president's nomination.
    reappointed = served.get(
        'Reappointing President', pd.Series('', index = served.index))
    reappointed = reappointed.fillna('').str.strip()
    table['president'] = served['Appointing President'].where(
        reappointed == '', reappointed)
    table['party'] = served['Party of Appointing President'].where(
        reappointed == '',
        served.get(
            'Party of Reappointing President',
            pd.Series('', index = served.index)))
    reassigned = table['president'].str.startswith('None')
    table['reassigned'] = reassigned
    inherited = table[list(_INHERITED)].mask(reassigned)
    inherited = inherited.groupby(table['nid']).ffill()
    table[list(_INHERITED)] = inherited.where(
        reassigned, table[list(_INHERITED)]).fillna('')
    table['appointment_date'] = [
        nomination or recess or confirmation or commission
        for nomination, recess, confirmation, commission in zip(
            table['nomination_date'], table['recess_date'],
            table['confirmation_date'], table['commission_date'],
            strict = True)]
    table['circuit'] = table['court'].map(_circuit).astype('Int64')
    table['earlier'] = [
        tuple(group['court'].iloc[:position])
        for _, group in table.groupby('nid', sort = False)
        for position in range(len(group))]
    people = people.assign(nid = people['nid'].astype(int))
    people = people.drop_duplicates('nid').set_index('nid')
    names = {
        'jid': 'jid', 'last_name': 'Last Name', 'first_name': 'First Name',
        'middle_name': 'Middle Name', 'suffix': 'Suffix',
        'birth_state': 'Birth State'}
    for column, source in names.items():
        table[column] = table['nid'].map(people[source]).fillna('')
    table['jid'] = pd.to_numeric(table['jid'], errors = 'coerce').astype(
        'Int64')
    order = [
        'nid', 'jid', 'judge', 'last_name', 'first_name', 'middle_name',
        'suffix', 'sequence', 'court_type', 'court', 'title', 'circuit',
        'president', 'party', 'recess_date', 'nomination_date',
        'confirmation_date', 'commission_date', 'termination_date',
        'appointment_date', 'reassigned', 'earlier', 'birth_state']
    return table[order]


def careers(
    career: pd.DataFrame | pathlib.Path | str) -> dict[int, list[str]]:
    """Returns the entries of each judge's career, in the file's order.

    Args:
        career: the file of professional careers, as a path or a table.

    Raises:
        KeyError: if the file lacks a column that is needed.

    Returns:
        The entries of each judge (such as "Private practice, Houston, Texas,
            1970-1985"), by the judge's "nid".

    """
    entries = _read(career)
    _require(
        entries, ['nid', 'Professional Career'],
        'the file of professional careers')
    numbers = entries['nid'].astype(int)
    return {
        int(nid): group.tolist()
        for nid, group in entries['Professional Career'].groupby(
            numbers, sort = False)}


""" Private Functions """


def _circuit(court: str) -> int | None:
    """Returns the number of a court of appeals.

    Args:
        court: the name of a court, such as "U.S. Court of Appeals for the
            Fifth Circuit".

    Returns:
        The number of the court of appeals, or `None` for any other court.

    """
    if not court.startswith('U.S. Court of Appeals for the '):
        return None
    for words, number in _ORDINALS.items():
        if court == f'U.S. Court of Appeals for the {words} Circuit':
            return number
    return None


def _read(source: pd.DataFrame | pathlib.Path | str) -> pd.DataFrame:
    """Returns a table from a table or a CSV file.

    Args:
        source: a table (which is copied) or the path of a CSV file.

    Returns:
        The table, with every cell as text and blanks for missing cells.

    """
    if isinstance(source, pd.DataFrame):
        return source.copy().fillna('').astype(str)
    return utilities.read_csv(source, dtype = str, keep_default_na = False)


def _require(
    data: pd.DataFrame,
    columns: list[str],
    name: str) -> None:
    """Raises an error if a table lacks columns.

    Args:
        data: the table.
        columns: names of the columns that are needed.
        name: what the table is, for the message.

    Raises:
        KeyError: if a column is missing.

    """
    missing = [column for column in columns if column not in data.columns]
    if missing:
        message = f'{name} needs the columns {missing}, which are missing'
        raise KeyError(message)
