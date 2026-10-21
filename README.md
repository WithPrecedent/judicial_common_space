# judicial_common_space

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/judicial-common-space.svg?style=for-the-badge&color=cornflowerblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/judicial-common-space/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/judicial_common_space?style=for-the-badge&color=forestgreen&label=GitHub&logo=github)](https://github.com/WithPrecedent/judicial_common_space/releases) |
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/judicial_common_space/ci.yml?branch=main&style=for-the-badge&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/judicial_common_space/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=for-the-badge&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/judicial-common-space?style=for-the-badge&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/judicial_common_space/) |
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=for-the-badge&color=forestgreen&logo=github)](https://WithPrecedent.github.io/judicial_common_space) |
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=for-the-badge&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=for-the-badge&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/uv-mediumpurple?style=for-the-badge&logo=uv&labelColor=gray)](https://docs.astral.sh/uv/) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-forestgreen?style=for-the-badge&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=for-the-badge&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-forestgreen?style=for-the-badge&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot) |
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/judicial-common-space?style=for-the-badge&color=cornflowerblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/judicial_common_space/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=for-the-badge&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-antiquewhite?style=for-the-badge&logo=apple&labelColor=gray)](https://www.apple.com/macos/)  [![Windows](https://img.shields.io/badge/Windows-blue?style=for-the-badge)](https://www.microsoft.com/en-us/windows?r=1) |
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/judicial-common-space?style=for-the-badge&color=cornflowerblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/judicial-common-space) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/judicial_common_space?style=for-the-badge&color=forestgreen&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/judicial_common_space/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/judicial_common_space?style=for-the-badge&color=forestgreen&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/judicial_common_space/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/judicial_common_space?style=for-the-badge&color=forestgreen&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/judicial_common_space/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/judicial_common_space?style=for-the-badge&color=forestgreen&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/judicial_common_space/forks) |
| | |

-----

## What is judicial_common_space?

`judicial_common_space` computes the Judicial Common Space (JCS) score of
every appointment of a federal judge who has served since 1953 (the first
year of the original study, or any year you choose), following Epstein,
Martin, Segal, and Westerland, ["The Judicial Common
Space,"](https://epstein.wustl.edu/s/JCS.pdf) 23 *J.L. Econ. & Org.* 303
(2007). It saves them in a spreadsheet with each judge's name, the
Federal Judicial Center's two numbers for the judge (`nid` and `jid`), and
the judge's score for each appointment, and checks them against the
published scores.

## Why use judicial_common_space?

The published JCS scores cover the judges of the courts of appeals and the
justices, with one score per judge and court, and are updated every few
years. This package:

- **Scores every Article III appointment**: district courts, courts of
  appeals, the Supreme Court, and the national courts (the Court of
  International Trade and the courts before it).
- **Scores each appointment separately**, because a judge's score depends
  on the president and senators of the appointment: a district judge
  elevated to a court of appeals gets a new score.
- **Uses the current sources**, downloaded when needed: the Federal Judicial
  Center's [Biographical Directory of Article III Federal
  Judges](https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export),
  [Voteview's](https://voteview.com/data) DW-NOMINATE scores, the
  [congress-legislators](https://github.com/unitedstates/congress-legislators)
  dates of senators' service, and the [Martin-Quinn
  scores](https://mqscores.wustl.edu/measures.php).
- **Shows its work**: each row says which state the judge was appointed
  from, how that was found, and which senators (or the president) the score
  came from.
- **Checks itself** against the published JCS scores of circuit judges and
  justices and against Christina Boyd's scores of district judges, which are
  made the same way.

## How the scores are made

The paper scores the lower courts by the rule of Giles, Hettinger, and
Peppers (2001), which follows the norm of senatorial courtesy. If a judge is
appointed from a state where the president and at least one senator are of
the same party, the judge gets that senator's NOMINATE score, or the mean of
the senators' scores. Otherwise the judge gets the president's score.
Justices get their Martin-Quinn score in each term, put on the same scale by
the paper's arctangent transformation: `2/π · arctan(b0 + b1 · MQ)`.

The package applies the rule this way:

| Step | How |
| --- | --- |
| Appointment | Each row of the center's file of federal judicial service. The senators and the president are those of the nomination (or of the recess appointment, if there was no nomination). A judge renominated by a new president after a recess appointment (as Roger Gregory was) is scored by the president who nominated the judge to the Senate. A judge moved to a court without an appointment (as the Fifth Circuit's judges were to the Eleventh in 1981) keeps the score of the appointment before. |
| Home state | A district judge's comes from the court's name. A circuit judge's is the state of a district court in the circuit that the judge served on before; or else of the job the judge held when appointed (or the most recent before), as the center's record of the judge's career names it; or else the judge's birth state, if it is in the circuit. Judges of the District of Columbia Circuit, the Federal Circuit, and the other national courts get the president's score, as they do in the published scores. |
| Senators | By default, every senator from the state who sat in the Congress of the appointment and belonged to the president's party, as the published scores count them (`--senators congress`). With `--senators date`, only the senators who held the seats on the day, by their party on that day, which is the rule as the paper states it and closer to Boyd's district scores. |
| Scores | Voteview's `nominate_dim1` for senators and presidents (one score for each member's whole service). |
| Justices | The arctangent transformation with the coefficients of the 2024 release of the JCS scores (b0 = 0.1934, b1 = 0.6025), recovered from its 782 justice-terms (r = 0.9998), because both scales have changed since the paper estimated b0 = −0.1736 and b1 = 0.461 from the scores of 2005 (`--transformation paper` uses those). A justice's appointment gets the score of its first term, and the "Justices" sheet has every term. |

## How well they match the published scores

With the default settings, against the [JCS 2024
release](https://epstein.wustl.edu/jcs) and [Boyd's district court
scores](https://sites.wustl.edu/clboyd/research) (through the 118th
Congress):

| Check | Published | Found | Same (within 0.0005) | Same or within 0.02 | Correlation |
| --- | ---: | ---: | ---: | ---: | ---: |
| Circuit judges (JCS 2024) | 705 | 703 | 88.2% | 96.6% | 0.997 |
| District judges (Boyd) | 2,615 | 2,615 | 83.6% | 95.4% | 0.998 |
| Justice-terms (JCS 2024) | 782 | 782 | 24.9% | 99.4% | 1.000 |

With `--senators date`, the district judges match Boyd's scores 99.2% of the
time (within 0.02) and the circuit judges match the JCS scores 92.9% of the
time, so the two published sources count senators differently.

Most differences under 0.02 are not errors. Voteview re-estimates the score
of every member who is still serving whenever it adds a Congress, so judges
whose senators are still in office (Fetterman, Rick Scott, Hickenlooper, and
others) drift a little from scores published with an older file. The same is
true of recent justices in the Martin-Quinn scores. The larger differences
that remain are judges whose home state the center's records do not show
(such as J. Michael Luttig and Julie Rikelman), a few D.C. Circuit judges and
the Federal Circuit judges who came from the Court of Customs and Patent
Appeals, which the published file scores differently, and some apparent
slips in the published files. The spreadsheet's check sheets list every
comparison.

## Getting started

### Requirements

- Python 3.11 or later
- An internet connection, the first time, to download the source files
  (about 25 megabytes)

### Installation

To install `judicial_common_space`, use `pip`:

```sh
pip install judicial-common-space
```

### Usage

From the command line:

```sh
judicial-common-space --output judicial_common_space.xlsx
```

Or from Python:

```python
import judicial_common_space

judicial_common_space.run('judicial_common_space.xlsx', start_year = 1953)
```

| Option | Default | Description |
| --- | --- | --- |
| `--output` | `judicial_common_space.xlsx` | Where to save the spreadsheet. |
| `--start-year` | `1953` | Include judges who served on a court in this year or later, and the justices' terms from the one sitting in January of that year. The default is the first year of the original study, which covered 1953 through 2000; the published scores now run through 2024, and these through the latest data. |
| `--senators` | `congress` | Which senators count: `congress` (as the published scores do) or `date` (those holding the seats on the day). |
| `--transformation` | `jcs2024` | How Martin-Quinn scores are put on the scale: `jcs2024` or `paper`. |
| `--martin-quinn` | the data folder's | The Martin-Quinn `justices.csv`, if it cannot be downloaded. The Martin-Quinn site checks for automated browsers, so if the download fails, save the file from its page and pass its path (or put it in the data folder's `politics` folder). |
| `--data-folder` | `data/courts` beside the code folder | Where the downloads are kept: the same folders that [courtpy](https://github.com/WithPrecedent/courtpy) uses, so the projects share them. Set `JUDICIAL_COMMON_SPACE_DATA_DIR` to change it for good. |
| `--overwrite` | off | Download the files again, as when the center has added judges or Voteview has added votes. |
| `--no-download` | off | Use only the files that are already there. |
| `--no-check` | off | Do not compare the scores with the published scores. |

The spreadsheet has these sheets:

| Sheet | Contents |
| --- | --- |
| Scores | A row for each appointment: `judge`, `nid`, `jid`, the court, the president and party, the dates, the Congress, `home_state` and `state_source`, `method` and `senators` (how the score was found), `president_score`, and `jcs`. |
| Justices | Each justice's Martin-Quinn and JCS scores in each term. |
| Verification | The agreement with each set of published scores. |
| Circuit check, District check, Justice check | Every comparison, with both scores and how the computed one was found. |
| About | The method, the sources, and the settings. |

## Contributing

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/judicial_common_space/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/judicial_common_space/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/judicial_common_space/code_of_conduct.md).

## Similar Projects

* [courtpy](https://github.com/WithPrecedent/courtpy) adds the published JCS
  scores (and the other measures here) to court cases, and shares this
  package's downloads.
* The [JCS scores](https://epstein.wustl.edu/jcs) of Lee Epstein, Andrew D.
  Martin, Jeffrey A. Segal, and Chad Westerland, for the judges of the courts
  of appeals and the justices.
* Christina L. Boyd's [Federal District Court Judge Ideology
  Data](https://sites.wustl.edu/clboyd/research), which scores district
  judges by the same rule.

## Acknowledgments

The scores rest on the work and data of Epstein, Martin, Segal, and
Westerland; Micheal W. Giles, Virginia A. Hettinger, and Todd Peppers; Keith
T. Poole, Howard Rosenthal, and Voteview; Andrew D. Martin and Kevin M. Quinn;
the Federal Judicial Center; the contributors to congress-legislators; and
Christina L. Boyd. Please cite them when you use the scores.

This project was generated from [@WithPrecedent](https://github.com/WithPrecedent)'s [![cookiecutter Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) template.

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/judicial_common_space/blob/main/LICENSE).
