"""Weather file parsing functions.
"""

# TODO: Split up station name into city, province, country?
# TODO: Parse out data source (CWEC2016) from location line, or is it fixed?

import re
import datetime


def get_wx_file_info(wx_file):
    """Parse a weather file (.epw) and return essential info, namely the information
    that characterizes its station and the weather file data. Some of this information
    is externally determined or determined from its filename.
    """
    file_info = parse_file_name(wx_file.name)
    time_period_centre = get_time_period_centre(file_info["timePeriod"])
    line = wx_file.readline()
    location_part, morphed, file_version, creation_date_part = line.split(' | ')

    station = parse_location_part(location_part)

    wx_file = {
        "creationDate": parse_creation_date_part(creation_date_part),
        "dataSource": file_info["dataSource"],
        "designDataType": "TMY",
        "scenario": "RCP8.5",
        "timePeriodCentre": time_period_centre,
        "ensembleStatistic": "average",
    }

    return station, wx_file


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
    regex = re.compile(
        r"LOCATION,(?P<name>.*),CWEC2016,(?P<code>\w+),(?P<lat>-?\d+\.\d+),"
        r"(?P<lon>-?\d+\.\d+),(?P<tz>-?\d+\.\d+),(?P<elev>-?\d+\.\d+)"
    )
    match = regex.match(part)
    if match:
        return {
            "name": match.group("name"),
            "code": match.group("code"),
            "longitude": float(match.group("lon")),
            "latitude": float(match.group("lat")),
            "elevation": float(match.group("elev")),
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
