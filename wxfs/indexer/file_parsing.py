"""Weather file parsing functions.
"""

import re
import datetime
import logging


logger = logging.getLogger(__name__)


def get_wx_file_info(
    wx_file,
    ver1_metadata_sep=" | ",
    ver2_metadata_prefix="COMMENTS 2",
    ver2_metadata_max_line_number=10,
):
    """Parse a weather file (.epw) and return essential info, namely the information
    that characterizes its location and the weather file data. Some of this information
    is externally determined or determined from its filename.
    """
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

        line_num = 1
        while not line.startswith(ver2_metadata_prefix):
            line_num += 1
            if line_num > ver2_metadata_max_line_number:
                logger.error(
                    f"Neither ver 1 nor ver 2 metadata indicators found in file"
                )
                return None, None
            line = wx_file.readline()
        # There's actually more than creation date in this line,
        # but we don't care, parser is up to it.
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
            "scenario": "RCP8.5",
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
    match = regex.search(part)
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
    return year + 5
