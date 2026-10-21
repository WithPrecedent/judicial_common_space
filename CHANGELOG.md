# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## Unreleased

* Computed the Judicial Common Space score of every appointment of a federal
  judge who served since 1953 (the first year of Epstein et al.'s study),
  from the Federal Judicial Center's
  Biographical Directory, Voteview's DW-NOMINATE scores, the dates of
  senators' service, and the Martin-Quinn scores
* Saved the scores in a spreadsheet with both of the center's numbers for
  each judge (`nid` and `jid`)
* Checked the scores against the published JCS scores of circuit judges and
  justices and Christina Boyd's scores of district judges
* Added the `judicial-common-space` command
* Found the home states of circuit judges whose careers show none from their
  duty stations in Wikipedia's articles on the courts of appeals, and added
  the `duty_station` column

## 0.1.0
    Initial Commit
