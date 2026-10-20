"""Settings and reference tables that judicial_common_space uses.

Contents:
    _ARCTANGENT: the intercept and slope of the transformation of
        Martin-Quinn scores into the Judicial Common Space (Epstein et al.'s
        equation 2): "paper" for the article's, and "jcs2024" for those of
        the 2024 release of the scores.
    _BOYD_URL: address of Christina Boyd's scores of district judges, which
        `verify` compares the district judges' scores with.
    _CIRCUIT_STATES: the states and territories of each regional circuit.
    _DATA_FOLDER: the folder where downloads are kept when no other is named.
    _DC_AGENCIES: patterns for jobs in the federal government in Washington,
        D.C., which career entries name without naming the city.
    _DC_PLACES: patterns that name Washington, D.C.
    _ENV_DATA: the environment variable that names another data folder.
    _FJC_FILES: the Federal Judicial Center's files that are used.
    _FJC_URL: address of the folder with the Federal Judicial Center's files.
    _JCS_PAGE: address of the page that links to the current archive of
        Judicial Common Space scores.
    _JCS_FILES: patterns for the names of the files in that archive.
    _LEGISLATORS_FILES: the files of the dates that senators served.
    _LEGISLATORS_URL: address of the folder with those files.
    _MINOR_POSITIONS: pattern for career entries that do not show where a
        judge lived, such as visiting professorships.
    _MQ_FILE: name of the file of each justice's Martin-Quinn score in each
        term.
    _MQ_PAGE: address of the page that links to it.
    _NATIONAL_COURTS: the courts with national jurisdiction, whose judges have
        no home state.
    _OLD_FIFTH: the states of the Fifth Circuit before the Eleventh Circuit
        was made from it.
    _PARTY_CODES: Voteview's codes for the parties of presidents.
    _PLACES: patterns for cities and schools that career entries name without
        naming their states.
    _PRESIDENTS: Voteview's number (ICPSR) for each president since McKinley,
        by the name that the Federal Judicial Center gives the president.
    _SPLIT_FIFTH: the day the Fifth Circuit was divided.
    _START_YEAR: the first year of service that is included by default.
    _STATES: the names of the states and territories, by their postal codes.
    _TERRITORIES: the places with federal courts that have no senators.
    _TIMEOUT: the number of seconds to wait for a server.
    _USER_AGENT: how judicial_common_space identifies itself to servers.
    _VOTEVIEW_FILE: name of Voteview's file of the ideology of every member.
    _VOTEVIEW_URL: address of the folder with that file.

"""

from __future__ import annotations

import pathlib
import re

# Epstein et al. estimated the transformation in 2007 from the scales of that
# time. Both scales have changed since, and the 2024 release of the scores
# used a new estimate that it does not report: these are its intercept and
# slope, recovered by regressing tan(pi / 2 * JCS) on the Martin-Quinn score
# of each of its 782 justice-terms (r = 0.9998).
_ARCTANGENT: dict[str, tuple[float, float]] = {
    'jcs2024': (0.1934, 0.6025),
    'paper': (-0.1736, 0.461)}
_BOYD_URL: str = (
    'https://www.dropbox.com/scl/fi/g4vjqf26w9xn1ujc5vbww/'
    'Boyd-district-court-ideology-scores-through-118th-Cong-Aug2025.csv'
    '?rlkey=phjle9lyf3yadbbeyfs0iud57&dl=1')
_CIRCUIT_STATES: dict[int, tuple[str, ...]] = {
    1: ('ME', 'MA', 'NH', 'PR', 'RI'),
    2: ('CT', 'NY', 'VT'),
    3: ('DE', 'NJ', 'PA', 'VI'),
    4: ('MD', 'NC', 'SC', 'VA', 'WV'),
    5: ('CZ', 'LA', 'MS', 'TX'),
    6: ('KY', 'MI', 'OH', 'TN'),
    7: ('IL', 'IN', 'WI'),
    8: ('AR', 'IA', 'MN', 'MO', 'NE', 'ND', 'SD'),
    9: ('AK', 'AZ', 'CA', 'GU', 'HI', 'ID', 'MP', 'MT', 'NV', 'OR', 'WA'),
    10: ('CO', 'KS', 'NM', 'OK', 'UT', 'WY'),
    11: ('AL', 'FL', 'GA'),
    12: ('DC',)}
# "data/courts" two folders above the repository (beside the folder of code
# projects), where courtpy and fjc-idb keep their court data too.
_DATA_FOLDER: pathlib.Path = (
    pathlib.Path(__file__).parents[4] / 'data' / 'courts')
_DC_AGENCIES: re.Pattern[str] = re.compile(
    r'U\.S\. Department of|Department of Justice|Solicitor General|'
    r'Office of Legal Counsel|White House|Executive Office of the President|'
    r'Federal Trade Commission|Securities and Exchange Commission|'
    r'Federal Communications Commission|U\.S\. Senate|Senate Judiciary|'
    r'U\.S\. House of Representatives|Supreme Court of the United States|'
    r'Georgetown|George Washington University|Howard University|'
    r'American University|Catholic University')
_DC_PLACES: re.Pattern[str] = re.compile(
    r'Washington,? D\.? ?C\.?|District of Columbia|D\.C\. Circuit')
_ENV_DATA: str = 'JUDICIAL_COMMON_SPACE_DATA_DIR'
# The files of the Biographical Directory of Article III Federal Judges that
# are organized by category, by what `sources.download` calls each.
_FJC_FILES: dict[str, str] = {
    'service': 'federal-judicial-service.csv',
    'demographics': 'demographics.csv',
    'career': 'professional-career.csv'}
_FJC_URL: str = 'https://www.fjc.gov/sites/default/files/history/'
_JCS_FILES: dict[str, str] = {
    'judges': r'coa_judges',
    'justices': r'supreme_court.*long',
    'medians': r'medians'}
_JCS_PAGE: str = 'https://epstein.wustl.edu/jcs'
_LEGISLATORS_FILES: dict[str, str] = {
    'legislators_historical': 'legislators-historical.json',
    'legislators_current': 'legislators-current.json'}
_LEGISLATORS_URL: str = 'https://unitedstates.github.io/congress-legislators/'
_MINOR_POSITIONS: re.Pattern[str] = re.compile(
    r'^\s*(Visiting|Adjunct|Lecturer|Instructor|Member|Board member|Trustee|'
    r'Fellow|Faculty fellow|Consultant|Chair, U\.S\. Sentencing|'
    r'Commissioner, U\.S\. Sentencing|U\.S\. (Army|Navy|Marine|Air|Coast)|'
    r'U\.S\. Naval|U\.S\. Army)',
    re.IGNORECASE)
_MQ_FILE: str = 'justices.csv'
_MQ_PAGE: str = 'https://mqscores.wustl.edu/measures.php'
_NATIONAL_COURTS: tuple[str, ...] = (
    'Federal Circuit', 'Court of International Trade', 'Customs Court',
    'Court of Claims', 'Court of Customs and Patent Appeals',
    'Commerce Court', 'Emergency Court of Appeals')
_OLD_FIFTH: tuple[str, ...] = ('AL', 'CZ', 'FL', 'GA', 'LA', 'MS', 'TX')
_PARTY_CODES: dict[str, int] = {'Democratic': 100, 'Republican': 200}
# Places named without their states. A state that an entry names comes before
# these, so "Columbia, South Carolina" is South Carolina, not New York.
_PLACES: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern), state) for pattern, state in (
        (r'\bHarvard\b|\bBoston\b|\bTufts\b', 'MA'),
        (r'\bYale\b|\bNew Haven\b|\bHartford\b', 'CT'),
        ((r'\bColumbia (Law|University|College)|\bFordham\b|\bCornell\b|'
          r'\bNew York City\b|\bManhattan\b|\bBrooklyn\b|\bBronx\b'), 'NY'),
        (r'\bPrinceton\b|\bRutgers\b|\bSeton Hall\b', 'NJ'),
        ((r'\bPhiladelphia\b|\bPittsburgh\b|\bVillanova\b|'
          r'\bTemple University\b|\bDuquesne\b'), 'PA'),
        (r'\bBaltimore\b', 'MD'),
        (r'\bDuke\b|\bWake Forest\b', 'NC'),
        (r'\bAtlanta\b|\bEmory\b', 'GA'),
        (r'\bMiami\b', 'FL'),
        (r'\bNew Orleans\b|\bTulane\b|\bBaton Rouge\b', 'LA'),
        ((r'\bHouston\b|\bDallas\b|\bSan Antonio\b|\bFort Worth\b|'
          r'\bSouthern Methodist\b'), 'TX'),
        (r'\bDetroit\b|\bAnn Arbor\b', 'MI'),
        (r'\bCleveland\b|\bCincinnati\b', 'OH'),
        (r'\bNashville\b|\bVanderbilt\b|\bMemphis\b', 'TN'),
        (r'\bLouisville\b', 'KY'),
        (r'\bChicago\b|\bNorthwestern (University|Law)', 'IL'),
        (r'\bNotre Dame\b|\bIndianapolis\b', 'IN'),
        (r'\bMilwaukee\b|\bMarquette\b', 'WI'),
        (r'\bSt\. Louis\b|\bSaint Louis\b|\bWashington University\b', 'MO'),
        (r'\bMinneapolis\b|\bSt\. Paul\b', 'MN'),
        (r'\bDenver\b', 'CO'),
        (r'\bPhoenix\b|\bTucson\b', 'AZ'),
        (r'\bSalt Lake City\b|\bBrigham Young\b', 'UT'),
        ((r'\bStanford\b|\bLos Angeles\b|\bSan Francisco\b|\bSan Diego\b|'
          r'\bBerkeley\b|\bUCLA\b|\bSacramento\b'), 'CA'),
        (r'\bSeattle\b', 'WA')))
_PRESIDENTS: dict[str, int] = {
    'William McKinley': 99892,
    'Theodore Roosevelt': 99893,
    'William H. Taft': 99894,
    'Woodrow Wilson': 99895,
    'Warren G. Harding': 99896,
    'Calvin Coolidge': 99897,
    'Herbert Hoover': 99898,
    'Franklin D. Roosevelt': 99899,
    'Harry S Truman': 99900,
    'Dwight D. Eisenhower': 99901,
    'John F. Kennedy': 99902,
    'Lyndon B. Johnson': 99903,
    'Richard M. Nixon': 99904,
    'Gerald Ford': 99905,
    'Jimmy Carter': 99906,
    'Ronald Reagan': 99907,
    'George H.W. Bush': 99908,
    'William J. Clinton': 99909,
    'George W. Bush': 99910,
    'Barack Obama': 99911,
    'Donald J. Trump': 99912,
    'Joseph R. Biden': 99913}
_SPLIT_FIFTH: str = '1981-10-01'
_START_YEAR: int = 1950
_STATES: dict[str, str] = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
    'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
    'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan',
    'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
    'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota',
    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
    'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming',
    'DC': 'District of Columbia', 'PR': 'Puerto Rico',
    'VI': 'Virgin Islands', 'GU': 'Guam', 'CZ': 'Canal Zone',
    'MP': 'Northern Mariana Islands'}
_TERRITORIES: frozenset[str] = frozenset({'CZ', 'DC', 'GU', 'MP', 'PR', 'VI'})
_TIMEOUT: int = 120
_USER_AGENT: str = (
    'judicial_common_space '
    '(https://github.com/WithPrecedent/judicial_common_space)')
_VOTEVIEW_FILE: str = 'HSall_members.csv'
_VOTEVIEW_URL: str = 'https://voteview.com/static/data/out/members/'
