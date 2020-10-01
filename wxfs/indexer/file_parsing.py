"""Weather file parsing functions.
"""

# TODO: Split up location name into city, province, country?
# TODO: Parse out data source (CWEC2016) from location line, or is it fixed?

import re
import datetime


def get_wx_file_info(wx_file):
    """Parse a weather file (.epw) and return essential info, namely the information
    that characterizes its location and the weather file data. Some of this information
    is externally determined or determined from its filename.
    """
    file_info = parse_file_name(wx_file.name)
    time_period_centre_year = get_time_period_centre(file_info["timePeriod"])
    line = wx_file.readline()
    location_part, morphed, file_version, creation_date_part = line.split(' | ')

    location = parse_location_part(location_part)

    wx_file = {
        "creationDate": parse_creation_date_part(creation_date_part),
        "dataSource": file_info["dataSource"],
        "designDataType": "TMY",
        "scenario": "RCP8.5",
        "timePeriodStart":
            datetime.datetime(time_period_centre_year-15, 1, 1),
        "timePeriodEnd":
            datetime.datetime(time_period_centre_year+15, 1, 1) -
            datetime.timedelta(seconds=1),
        "ensembleStatistic": "average",
        "variables": "all thermodynamic",
        "anomaly": "daily",
        "smoothing": 21
    }

    return location, wx_file


def parse_file_name(name):
    """Parse out info from the file name of a PCIC EPW file."""
    regex = re.compile(
        r"(?P<timePeriod>\d{4}s)_(?P<country>\w+)_(?P<province>\w+)_(?P<city>.+)"
        r"\.(?P<code>\d+)_(?P<dataSource>\w+)\.[eE][pP][wW]"
    )
    match = regex.search(name)
    if match:
        return {
            "timePeriod": match.group("timePeriod"),
            "country": match.group("country"),
            "province": match.group("province"),
            "city": match.group("city"),
            "code": match.group("code"),
            "dataSource": match.group("dataSource"),
        }
    return None


def parse_location_part(part):
    """Parse the location part of the first line of a PCIC EPW file."""
    location_regex = re.compile(
        r"LOCATION,(?P<city>[^,]+),(?P<province>[^,]+),(?P<country>[^,]+),CWEC2016,"
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
    match = regex.match(part)
    if match:
        return datetime.datetime.strptime(match.group("date"), "%Y-%m-%d")
    return None


def get_time_period_centre(time_period):
    """
    Return the centre year of a time period with a designator of the form
        <year>s
    where <year> is a 4-digit year multiple of 10 (e.g., "2050s").
    """
    year = int(time_period[0:4])
    return year + 5;
