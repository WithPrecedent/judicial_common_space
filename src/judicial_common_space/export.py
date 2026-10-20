"""Writes the scores and their checks to a spreadsheet.

| Sheet | Contents |
| --- | --- |
| "Scores" | A row for each appointment (see `scores.appointments`). |
| "Justices" | Each justice's score in each term (see `scores.justices`), if there were Martin-Quinn scores. |
| "Verification" | The agreement with each set of published scores (see `verify.summarize`). |
| "Circuit check", "District check", "Justice check" | The comparison of each judge or justice (see `verify`). |
| "About" | How the scores were made, and their sources. |

Contents:
    write: writes the spreadsheet.
    _ABOUT: the lines of the "About" sheet.

"""

from __future__ import annotations

import pathlib
from collections.abc import Mapping

import pandas as pd

_ABOUT: tuple[str, ...] = (
    'Judicial Common Space scores of federal judges, by appointment.',
    '',
    (
        'Method: Epstein, Martin, Segal & Westerland, "The Judicial Common '
        'Space," 23 J.L. Econ. & Org. 303 (2007), which scores lower-court '
        'judges by the rule of Giles, Hettinger & Peppers (2001): a judge '
        "appointed from a state with at least one senator of the president's "
        "party gets that senator's NOMINATE score (or the mean of those "
        "senators' scores); otherwise the judge gets the president's score. "
        'Justices get 2/pi * arctan(b0 + b1 * Martin-Quinn score) in each '
        'term.'),
    (
        'A judge is scored for each appointment, so a judge who was elevated '
        'has a score for each court. A judge moved to a court without an '
        'appointment (as from the Fifth Circuit to the Eleventh in 1981) '
        'keeps the score of the appointment before.'),
    (
        'Home states: district judges by the court; judges of the courts of '
        'appeals by an earlier district court in the circuit, then by their '
        'careers when appointed (Federal Judicial Center), then by their '
        'birth states. Judges of the District of Columbia Circuit, the '
        "Federal Circuit, and other national courts get the president's "
        'score.'),
    '',
    (
        'Sources: Federal Judicial Center, Biographical Directory of Article '
        'III Federal Judges (nid and jid are its numbers for each judge); '
        'Voteview, DW-NOMINATE scores of members of Congress and presidents '
        "(nominate_dim1); congress-legislators (dates of senators' service); "
        "Martin & Quinn, justices' scores; for verification, Epstein et al., "
        'Judicial Common Space scores (2024), and Christina L. Boyd, Federal '
        'District Court Judge Ideology Data (2025).'))


def write(
    path: pathlib.Path | str,
    sheets: Mapping[str, pd.DataFrame],
    settings: Mapping[str, object] | None = None) -> pathlib.Path:
    """Writes the scores and their checks to a spreadsheet.

    Args:
        path: where to save the spreadsheet (an Excel ".xlsx" file). Its
            folder is created if needed.
        sheets: the tables to write, by the name of each sheet. Empty
            tables are left out.
        settings: the settings that the scores were made with, which are
            listed on the "About" sheet. Defaults to `None`.

    Returns:
        `path`.

    """
    path = pathlib.Path(path).expanduser()
    path.parent.mkdir(parents = True, exist_ok = True)
    about = list(_ABOUT)
    if settings:
        about += ['', 'Settings:']
        about += [f'{name}: {value}' for name, value in settings.items()]
    with pd.ExcelWriter(path, engine = 'openpyxl') as writer:
        for name, table in sheets.items():
            if table is None or table.empty:
                continue
            table.to_excel(writer, sheet_name = name, index = False)
            sheet = writer.sheets[name]
            sheet.freeze_panes = 'A2'
            for number, column in enumerate(table.columns, start = 1):
                values = table[column].astype(str).str.len()
                width = max(len(str(column)), int(values.quantile(0.9))) + 2
                letter = sheet.cell(row = 1, column = number).column_letter
                sheet.column_dimensions[letter].width = min(width, 60)
        pd.DataFrame({'About': about}).to_excel(
            writer, sheet_name = 'About', index = False)
        writer.sheets['About'].column_dimensions['A'].width = 120
    return path
