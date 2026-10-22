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

This package:

- **Scores every Article III appointment**: district courts, courts of
  appeals, and the Supreme Court.
- **Uses the current sources**, downloaded when needed: the Federal Judicial
  Center's [Biographical Directory of Article III Federal
  Judges](https://www.fjc.gov/history/judges/biographical-directory-article-iii-federal-judges-export),
  [Voteview's](https://voteview.com/data) DW-NOMINATE scores, the
  [congress-legislators](https://github.com/unitedstates/congress-legislators)
  dates of senators' service, the [Martin-Quinn
  scores](https://mqscores.wustl.edu/measures.php), and Wikipedia's articles
  on the courts of appeals (for circuit judges' duty stations).
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
| Home state | A district judge's comes from the court's name. A circuit judge's is the state of a district court in the circuit that the judge served on before; or else of the job the judge held when appointed (or the most recent before), as the center's record of the judge's career names it; or else of the judge's duty station, as Wikipedia's article on the court gives it; or else the judge's birth state, if it is in the circuit. The duty station comes after the career because it is where the judge sat, which is sometimes not where the judge came from, but it agrees with the state from the career for 98.5% of the judges who have both. (The state of the judge whom the appointee replaced, from the center's seat numbers, made the matches worse: a seat changes states about one time in five.) Judges of the District of Columbia Circuit, the Federal Circuit, and the other national courts get the president's score, as they do in the published scores. |
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
| Circuit judges (JCS 2024) | 705 | 703 | 88.3% | 96.9% | 0.998 |
| District judges (Boyd) | 2,615 | 2,615 | 83.6% | 95.4% | 0.998 |
| Justice-terms (JCS 2024) | 782 | 782 | 24.9% | 99.4% | 1.000 |

With `--senators date`, the district judges match Boyd's scores 99.2% of the
time (within 0.02) and the circuit judges match the JCS scores 93.2% of the
time, so the two published sources count senators differently.

Most differences under 0.02 are not errors. Voteview re-estimates the score
of every member who is still serving whenever it adds a Congress, so judges
whose senators are still in office (Fetterman, Rick Scott, Hickenlooper, and
others) drift a little from scores published with an older file. The same is
true of recent justices in the Martin-Quinn scores. The larger differences
that remain are judges whom the published file places in a state that
neither the center's records nor Wikipedia show (such as Richard Cudahy in
Illinois and Stephen Trott in Idaho), a few D.C. Circuit judges and the
Federal Circuit judges who came from the Court of Customs and Patent
Appeals, which the published file scores differently, and some possible
slips in the published files. The spreadsheet's check sheets list every
comparison, and the next section explains every one that differs by more
than 0.05.

## Where they differ

These are every judge and justice whose computed score differs from the
published one by more than 0.05, with the default settings. (The 689 other
circuit judges, 2,529 district judges, and 780 justice-terms are within 0.05
of the published scores.)

### Circuit judges and Epstein et al.

| Judge | Circuit | Published | Computed | Why |
| --- | ---: | ---: | ---: | --- |
| Giles Rich | Fed. | 0.692 | 0.281 | Eisenhower appointed him to the Court of Customs and Patent Appeals, whose judges were moved to the new Federal Circuit in 1982. The published score is Reagan's, as if he were appointed then; the computed one is Eisenhower's. |
| John Nalbandian | 6th | 0.648 | 0.371 | The computed score is Ohio's Rob Portman's (Nalbandian practiced in Cincinnati, and Wikipedia gives Ohio as his duty station). The published one matches no Ohio senator and is the same as the two Florida judges' of 2019. |
| Richard Cudahy | 7th | −0.333 | −0.583 | The published score is Illinois's Adlai Stevenson III's. Cudahy's career and duty station were in Wisconsin. |
| Stephen Trott | 9th | 0.590 | 0.352 | The published score is Idaho's two senators', where Trott later sat. He came from California. |
| Jay Bybee | 9th | 0.693 | 0.508 | The published score is George W. Bush's. Bybee taught in Nevada, which is also his duty station, and Nevada's John Ensign was a Republican. |
| Morris Arnold | 8th | 0.381 | 0.557 | Arkansas's two senators were Democrats, so the computed score is the first President Bush's. The published one matches only Arizona's John McCain. |
| Karen Henderson | D.C. | 0.391 | 0.557 | The published score is South Carolina's Strom Thurmond's, where she had been a district judge. The published file gives every other D.C. Circuit judge who came from a district court the president's score. |
| Luther Swygert | 7th | −0.580 | −0.420 | He came from Indiana's district court, so the computed score is Indiana's Vance Hartke's. The published one is Illinois's Paul Douglas's. |
| James Browning | 9th | −0.461 | −0.311 | The published score is Montana's two senators', where he was born. The computed one is Washington's, from his last job in the circuit before he worked in Washington, D.C. |
| Howard Markey | Fed. | 0.692 | 0.552 | As with Rich: Reagan's score in the published file, and Nixon's, who appointed him, here. |
| John Hartigan | 1st | −0.299 | −0.391 | The published score is the mean of the two senators who held Rhode Island's seats when he was nominated. The computed one counts all four who sat in that Congress (`--senators date` gives the published score). |
| H. Nathan Swaim | 7th | −0.447 | −0.374 | The published score is Illinois's two senators'. He came from Indiana, whose senators were Republicans, so the computed score is Truman's. |
| Cindy Chung | 3rd | −0.313 | −0.245 | The published score is Bob Casey's alone; John Fetterman, who joined the Senate in 2023, was apparently not in the file it was made from. |
| Carl McGowan | D.C. | −0.405 | −0.472 | The published score matches no senators; the computed one is Kennedy's, as for other D.C. Circuit judges. |

### District judges and Boyd

75 of the 86 district judges who differ by more than 0.05 differ only
because of how senators are counted. By default, the score counts every
senator who sat in the Congress of the nomination; Boyd counts the senators
who held the seats on the day, as `--senators date` does, which gives every
one of these judges Boyd's score:

| State | Nominated | Judges | Boyd | Computed | Senators counted who did not hold the seats that day |
| --- | --- | ---: | ---: | ---: | --- |
| Alabama | 1938 | 1 | −0.275 | −0.336 | Hugo Black (left for the Supreme Court in 1937) |
| Alabama | 1945 | 1 | −0.275 | −0.177 | John Sparkman and George Swift (joined in 1946) |
| Alabama | 2018 | 5 | 0.446 | 0.518 | Jeff Sessions and Luther Strange (left in 2017 and January 2018) |
| Arkansas | 1937 | 1 | −0.302 | −0.228 | John E. Miller (joined after the nomination) |
| Arkansas | 1977 | 1 | −0.173 | −0.246 | Kaneaster Hodges (joined after the nomination) |
| Arkansas | 1978 | 1 | −0.378 | −0.246 | John McClellan (died in 1977) |
| California | 1950 | 1 | −0.374 | −0.263 | Sheridan Downey (resigned in 1950), so Boyd has Truman's score |
| California | 1964 | 1 | −0.462 | −0.341 | Clair Engle (died in 1964) |
| California | 2021–2022 | 12 | −0.345 | −0.473 | Kamala Harris (left in January 2021) |
| California | 2024 | 9 | −0.435 | −0.378 | Dianne Feinstein (died in 2023) and Adam Schiff (joined in December 2024) |
| Colorado | 1995–1996 | 2 | −0.438 | −0.141 | Ben Nighthorse Campbell (a Republican from March 1995), so Boyd has Clinton's score |
| Georgia | 1999 | 1 | −0.220 | −0.037 | Zell Miller (joined in 2000) |
| Indiana | 1943 | 1 | −0.115 | −0.248 | Samuel D. Jackson (joined in 1944) |
| Kentucky | 1939 | 1 | −0.384 | −0.318 | Happy Chandler (joined after the nomination) |
| Kentucky | 1946 | 1 | −0.375 | −0.281 | Happy Chandler (resigned in 1945) |
| Massachusetts | 2014 | 4 | −0.631 | −0.519 | John Kerry and Mo Cowan (left in 2013) |
| Missouri | 1945 | 1 | −0.258 | −0.309 | Harry Truman (left to be vice president) |
| New York | 1937–1938 | 2 | −0.243 | −0.311 | James Mead (joined in 1938) |
| New York | 1949 | 2 | −0.458 | −0.558 | Herbert Lehman (joined in November 1949) |
| New York | 1950 | 5 | −0.658 | −0.558 | Robert Wagner (resigned in 1949) |
| North Carolina | 1949 | 1 | −0.020 | −0.167 | Frank Graham and Willis Smith (joined after the nomination) |
| North Carolina | 1985 | 1 | 0.617 | 0.501 | James Broyhill (joined in 1986) |
| Oregon | 1937 | 1 | −0.368 | −0.490 | Alfred Reames (joined in 1938), so Boyd has Roosevelt's score |
| Rhode Island | 1950 | 1 | −0.299 | −0.391 | J. Howard McGrath and Edward Leahy (left the Senate before the nomination; Leahy is the judge) |
| South Carolina | 1941 | 2 | −0.212 | −0.297 | James Byrnes (left for the Supreme Court in 1941) |
| South Carolina | 1966 | 1 | −0.031 | −0.099 | Olin Johnston (died in 1965) |
| Texas | 1942 | 2 | 0.018 | −0.106 | Morris Sheppard (died in 1941) |
| Texas | 1962 | 4 | −0.416 | −0.155 | William Blakley (left in 1961) |
| Texas | 1993–1994 | 7 | −0.438 | −0.117 | Bob Krueger (left in June 1993), so Boyd has Clinton's score |
| Washington | 1939–1940 | 2 | −0.149 | −0.243 | Monrad Wallgren (joined in December 1940) |

The other 11 differ for reasons that seem to lie in Boyd's file:

| Judges | Boyd | Computed | Why |
| --- | ---: | ---: | --- |
| James Connell (Ohio, 1954) | 0.164 | 0.446 | Boyd's score is the mean of John Bricker's and Thomas Burke's, but Burke was a Democrat and Eisenhower a Republican. |
| John Cannella, Charles Tenney, Bernard Moynahan (New York and Kentucky, 1963), and Orrin Judd, Morris Lasker, Anthony Travia (New York, 1967–1968) | −0.337 | −0.472 | Boyd gives all six Lyndon Johnson's score. The first three were nominated by Kennedy, before his death; for the others, the senator of Johnson's party was Robert Kennedy, whose score is −0.472. |
| Cyrus Tavares (Hawaii, 1961) | 0.281 | 0.165 | Boyd gives Eisenhower's score, leaving out Hiram Fong, a Republican. |
| Leonard Stark (Delaware, 2010) | −0.353 | −0.281 | Boyd's score is the mean of Ted Kaufman's and Joe Biden's, who had left the Senate to be vice president. |
| Edmond Chang (Illinois, 2010) | −0.345 | −0.403 | Boyd leaves out Roland Burris, who held a seat until November 2010. |
| James Allred (Texas, 1939) | −0.219 | −0.275 | Unexplained: Boyd's score matches no Texas senators. |

### Justices and Epstein et al.

| Justice | Term | Published | Computed | Why |
| --- | ---: | ---: | ---: | --- |
| Ketanji Brown Jackson | 2022 | −0.444 | −0.577 | Her first term. The current Martin-Quinn scores, which include her later terms, estimate it again. |
| Clarence Thomas | 2022 | 0.648 | 0.701 | The same re-estimate of the 2022 term. |

### Using the published scores

`--use-published` (off by default) gives a judge or a justice's term the
published score wherever it differs from the computed one by more than 0.05
(or `--published-threshold`): Epstein et al.'s for circuit judges and
justices, and Boyd's for district judges. The Scores and Justices sheets
then say where each score came from (`jcs_source`) and keep the computed
score beside it (`computed_jcs`); the check sheets still compare the
computed scores. With the default settings, it replaces the scores of 95
appointments since 1953 (80 district judges, 14 circuit judges, and Justice
Jackson's appointment, from her first term) and of two justice-terms; with
`--senators date`, it replaces 46 (13 district judges, 32 circuit judges,
and Justice Jackson's).

Use it to reproduce the published scores, as when a study must line up with
earlier work that used them. It is off by default because:

* The two sources count senators differently (Boyd by the day, Epstein et al.
  by the Congress), so taking both mixes their rules: with either setting of
  `--senators`, one of them is overruled.
* Some of the published scores that it would take look like slips, such as
  John Nalbandian's, Morris Arnold's, James Connell's, and the six New York
  and Kentucky judges'.
* Only judges in the published files can be replaced, so judges appointed in
  the same circumstances can end up with scores made by different rules.
* The published scores were made with older Voteview files, so they lag
  behind the current scores of senators who are still serving.

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
| `--use-published` | off | Use the published score (Epstein et al.'s for circuit judges and justices, Boyd's for district judges) where it differs from the computed one by more than the threshold (see [Using the published scores](#using-the-published-scores)). |
| `--published-threshold` | `0.05` | The largest difference from a published score that keeps the computed score, with `--use-published`. |
| `--no-check` | off | Do not compare the scores with the published scores. |

The spreadsheet has these sheets:

| Sheet | Contents |
| --- | --- |
| Scores | A row for each appointment: `judge`, `nid`, `jid`, the court, the president and party, the dates, the Congress, `home_state` (a postal code) and `state_source` (how it was found), `duty_station` (Wikipedia's state for a circuit judge), `method` and `senators` (how the score was found), `president_score`, `computed_jcs`, `jcs`, and `jcs_source` ("computed", or with `--use-published`, "Epstein et al." or "Boyd"). |
| Justices | Each justice's Martin-Quinn and JCS scores in each term, with `computed_jcs` and `jcs_source`. |
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
the Federal Judicial Center; the contributors to congress-legislators and to
Wikipedia (whose text is available under the [Creative Commons
Attribution-ShareAlike License](https://creativecommons.org/licenses/by-sa/4.0/));
and Christina L. Boyd. Please cite them when you use the scores.

This project was generated from [@WithPrecedent](https://github.com/WithPrecedent)'s [![cookiecutter Template](https://img.shields.io/badge/snickerdoodle-bisque?style=for-the-badge&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/snickerdoodle) template.

## Citation

If you use `judicial_common_space` in your research, definitely cite these works:

```bibtex
@misc{boyd_district_2015,
  author = {Boyd, Christina L.},
  title  = {Federal District Court Judge Ideology Data},
  year   = {2015},
  url    = {http://cLboyd.net}
}

@article{epstein_jcs_2007,
  author  = {Epstein, Lee and Martin, Andrew D. and Segal, Jeffrey A. and Westerland, Chad},
  title   = {The Judicial Common Space},
  journal = {Journal of Law, Economics, and Organization},
  volume  = {23},
  number  = {2},
  pages   = {303--325},
  year    = {2007}
}

@article{giles_picking_2001,
  author  = {Giles, Micheal W. and Hettinger, Virginia A. and Peppers, Todd},
  title   = {Picking Federal Judges: A Note on Policy and Partisan Selection Agendas},
  journal = {Political Research Quarterly},
  volume  = {54},
  number  = {3},
  pages   = {623--641},
  year    = {2001}
}
```
And, although my contributions to the JCS project are relatively minor, feel free to cite the repository as well:

```bibtex
@software{yung_judicial_common_space,
  author  = {Yung, Corey Rayburn},
  title   = {judicial_common_space: Judicial Common Space scores for every Article III appointment},
  version = {0.1.0},
  year    = {2026},
  url     = {https://github.com/WithPrecedent/judicial_common_space},
  license = {Apache-2.0}
}

```
## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/judicial_common_space/blob/main/LICENSE).
