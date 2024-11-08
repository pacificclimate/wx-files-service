"""Weather file parsing functions.
"""

import re
import datetime
import logging


logger = logging.getLogger(__name__)


def get_wx_file_info(
    wx_file,
    ver1_metadata_sep=" | ",
    ver2_scenario_prefix="COMMENTS 1",
    ver2_creation_prefix="COMMENTS 2",
    ver2_metadata_max_line_number=10,
):
    """Parse a weather file (.epw) and return essential info, namely the information
    that characterizes its location and the weather file data. Some of this information
    is externally determined or determined from its filename.
    """
    scenario_part = None
    
    line = wx_file.readline()
    if ver1_metadata_sep in line:
        # This appears to contain version 1 format metadata
        try:
            location_part, _, _, creation_date_part = line.split(
                ver1_metadata_sep
            )
        except ValueError as e:
            logger.error(
                f"First line (listed below) contained ver 1 metadata separator "
                f"'{ver1_metadata_sep}' but it did not contain 4 parts. "
                f"\n{line}"
            )
            return None, None
    else:
        # Assume version 2 format metadata
        location_part = line
        
        creation_date_part = None


        line_num = 1
        while not creation_date_part or not scenario_part:
            line_num += 1
            if line_num > ver2_metadata_max_line_number:
                logger.error(
                    f"Neither ver 1 nor ver 2 metadata indicators found in file"
                )
                return None, None
            line = wx_file.readline()
            if line.startswith(ver2_scenario_prefix):
                scenario_part = line
            elif line.startswith(ver2_creation_prefix):
                creation_date_part = line


    location_info = parse_location_part(location_part)

    file_info = parse_file_name(wx_file.name)
    if file_info is not None:
        time_period_centre_year = get_time_period_centre(
            file_info["timePeriod"]
        )
        wx_file_info = {
            "creationDate": parse_creation_date_part(creation_date_part),
            "dataSource": file_info["dataSource"],
            "designDataType": "TMY",
            "scenario": parse_scenario_part(scenario_part),
            "timePeriodStart": datetime.datetime(
                time_period_centre_year - 15, 1, 1
            ),
            "timePeriodEnd": datetime.datetime(
                time_period_centre_year + 15, 1, 1
            )
            - datetime.timedelta(seconds=1),
            "ensembleStatistic": "average",
            "variables": "all thermodynamic",
            "anomaly": "daily",
            "smoothing": 21,
        }
    else:
        wx_file_info = None

    return location_info, wx_file_info


def parse_file_name(name):
    """Parse out info from the file name of a PCIC EPW file."""
    # this function is complicated by differences in CMIP5 and CMIP6 
    # versions of the data.
    # CMIP6 data has an emissions scenario in the filename, CMIP5 data 
    # has a numerical location code in the filename.
    cmip6 = "RCP" in name or "SSP" in name
    
    if cmip6:    
        scenario_start = name.find("RCP") if name.find("RCP") >= 0 else name.find("SSP")
        scenario_end = name.find("_", scenario_start)
        name = name[scenario_end + 1:]
        template = re.compile(
            r"(?P<timePeriod>\d{4}s)_(?P<country>\w+)_(?P<province>\w+)_(?P<city>.+)"
            r"\_(?P<dataSource>\w+)\.[eE][pP][wW]"
        )
    else:
        template = re.compile(
            r"(?P<timePeriod>\d{4}s)_(?P<country>\w+)_(?P<province>\w+)_(?P<city>.+)"
            r"\.(?P<code>\d+)_(?P<dataSource>\w+)\.[eE][pP][wW]"
        )
        
    match = template.search(name)
    if match:
        return {
            "timePeriod": match.group("timePeriod"),
            "country": match.group("country"),
            "province": match.group("province"),
            "city": match.group("city"),
            "code": "fakecode" if cmip6 else match.group("code"),
            "dataSource": match.group("dataSource"),
        }
    return None


def parse_location_part(part):
    """Parse the location part of the first line of a PCIC EPW file."""
    location_regex = re.compile(       
        r"LOCATION,(?P<city>[^,]+),(?P<province>[^,]+),(?P<country>[^,]+),CWEC20\d\d,"
        r"(?P<code>\w+),(?P<latitude>-?\d+\.\d+),(?P<longitude>-?\d+\.\d+),"
        r"(?P<tz>-?\d+\.\d+),(?P<elevation>-?\d+\.\d+)"
    )
    match = location_regex.match(part)
    if match:
        return {
            "city": match.group("city"),
            "province": match.group("province"),
            "country": match.group("country"),
            "code": match.group("code"),
            "longitude": float(match.group("longitude")),
            "latitude": float(match.group("latitude")),
            "elevation": float(match.group("elevation")),
        }
    return None


def parse_creation_date_part(part):
    """Parse the creation date part of the first line of a PCIC EPW file."""
    regex = re.compile(r"Creation Date:\s*(?P<date>\d{4}-\d{2}-\d{2})")
    match = regex.search(part)
    if match:
        return datetime.datetime.strptime(match.group("date"), "%Y-%m-%d")
    return None

def parse_scenario_part(part): 
    """Parse the emissions scenario from the comment line"""
    # just look for a word that starts either RCP or SSP.
    scenarios = {
        "RCP85": "RCP 8.5",
        "RCP45": "RCP 4.5",
        "RCP26": "RCP 2.6",
        "SSP126": "SSP1-2.6",
        "SSP245": "SSP2-4.5",
        "SSP585": "SSP5-8.5"
        }
    if part:
        for code in scenarios:
            if code in part:
                return scenarios[code]
    logger.info ("No scenario data found. Defaulting to RCP 8.5")
    return "RCP 8.5"

def get_time_period_centre(time_period):
    """
    Return the centre year of a time period with a designator of the form
        <year>s
    where <year> is a 4-digit year multiple of 10 (e.g., "2050s").
    """
    year = int(time_period[0:4])
    return year + 5

def summarize_attribute(files, attribute):
    """Used to populate metadata for summary files. Accepts a collection of files
    and the name of an attribute. If every file has the same_value for that 
    attribute, returns that value. Otherwise returns the string 'multiple'"""
    values = set([getattr(file, attribute) for file in files])
    
    if len(values) == 0:
        return None
    elif len(values) == 1:
        return list(values)[0]
    else:
        return "multiple"
    
    