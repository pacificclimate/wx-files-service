import pytest
import datetime
from wxfs.indexer.file_parsing import (
    get_wx_file_info,
    parse_file_name,
    parse_location_part,
    parse_creation_date_part,
    get_time_period_centre,
)

@pytest.mark.parametrize("year, city, code, lon, lat, elev", [
    (2020, "Anyville", "999999", 50.0, -124.5, 100.0),
    (2050, "Elsewhere", "11111", 51.1, -125.2, 1000.0),
])
def test_get_wx_file_info(year, city, code, lon, lat, elev, make_wx_file):
    with make_wx_file(year, city, code, lon, lat, elev) as wx_file:
        station_info, wx_file_info = get_wx_file_info(wx_file)
    assert station_info == {
        "name": f"{city},BC,CAN",
        "code": code,
        "longitude": lon,
        "latitude": lat,
        "elevation": elev,
    }
    assert wx_file_info == {
        "creationDate": datetime.datetime(2020, 6, 23),
        "dataSource": "CWEC2016",
        "designDataType": "TMY",
        "scenario": "RCP8.5",
        "timePeriodCentre": year + 5,
        "ensembleStatistic": "average",
    }


@pytest.mark.parametrize('input, expected', [
    (
        "/path/to/2050s_CAN_BC_Creston.717700_CWEC2016.epw",
        {
            "timePeriod": "2050s",
            "country": "CAN",
            "province": "BC",
            "city": "Creston",
            "code": "717700",
            "dataSource": "CWEC2016",
        }
    ),
    (
        "/path/to/2020s_CAN_BC_Abbotsford.Intl.AP.711080_CWEC2016.epw",
        {
            "timePeriod": "2020s",
            "country": "CAN",
            "province": "BC",
            "city": "Abbotsford.Intl.AP",
            "code": "711080",
            "dataSource": "CWEC2016",
        }
    ),
    (
        "/path/to/2050s_CAN_BC_Callaghan.Valley-Whistler.Olympic.Park.Ski.Resort.716880_CWEC2016.epw",
        {
            "timePeriod": "2050s",
            "country": "CAN",
            "province": "BC",
            "city": "Callaghan.Valley-Whistler.Olympic.Park.Ski.Resort",
            "code": "716880",
            "dataSource": "CWEC2016",
        }
    ),
])
def test_parse_file_name(input, expected):
    assert parse_file_name(input) == expected


@pytest.mark.parametrize('input, expected', [
    (
        "LOCATION,Burns Lake AP,BC,CAN,CWEC2016,719520,54.38320,-125.9587,-8.0,713.2",
        {
            "name": "Burns Lake AP,BC,CAN",
            "code": "719520",
            "longitude": -125.9587,
            "latitude": 54.38320,
            "elevation": 713.2,
        }
    ),
    (
        "LOCATION,Creston,BC,CAN,CWEC2016,717700,49.08170,-116.5007,-8.0,640.7",
        {
            "name": "Creston,BC,CAN",
            "code": "717700",
            "longitude": -116.5007,
            "latitude": 49.08170,
            "elevation": 640.7,
        }
    ),
])
def test_parse_location_part(input, expected):
    assert parse_location_part(input) == expected


@pytest.mark.parametrize('input, expected', [
    ("Creation Date: 2020-06-23", datetime.datetime(2020, 6, 23)),
])
def test_parse_creation_date_part(input, expected):
    assert parse_creation_date_part(input) == expected


@pytest.mark.parametrize('input, expected', [
    ("2020s", 2025),
    ("2050s", 2055),
])
def test_get_time_period_centre(input, expected):
    assert get_time_period_centre(input) == expected
