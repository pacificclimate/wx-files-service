import pytest

import datetime

from wxfs.indexer import index_wx_file
from wxfs.database import Location, WxFile, Version


@pytest.mark.parametrize(
    "year, city, code, lon, lat, elev",
    [
        (2020, "Anyville", "999999", 50.0, -124.5, 100.0),
        (2050, "Elsewhere", "11111", 51.1, -125.2, 1000.0),
    ],
)
@pytest.mark.parametrize("version", ["cmip5", "cmip6"])
def test_index_one_wx_file(year, city, code, lon, lat, elev, version, db_session, make_wx_file):
    wx_file_file_path = make_wx_file(year, city, code, lon, lat, elev)
    index_wx_file(db_session, version, wx_file_file_path)

    location = db_session.query(Location).one()
    assert location.city == city
    assert location.province == "BC"
    assert location.country == "CAN"
    assert location.code == code
    assert float(location.longitude) == lon
    assert float(location.latitude) == lat
    assert float(location.elevation) == elev

    ver = db_session.query(Version).one()
    assert ver.name == version 

    wx_file = db_session.query(WxFile).one()
    assert wx_file.location == location
    assert wx_file.creationDate == datetime.datetime(2020, 6, 23)
    assert wx_file.dataSource == "CWEC2016"
    assert wx_file.designDataType == "TMY"
    assert wx_file.scenario == "RCP85"
    print("timePeriodStart", wx_file.timePeriodStart)
    assert wx_file.timePeriodStart.year == year - 10
    print("timePeriodEnd", wx_file.timePeriodEnd)
    assert wx_file.timePeriodEnd.year == year + 19
    assert wx_file.ensembleStatistic == "average"


@pytest.mark.parametrize(
    "years, city, code, lon, lat, elev",
    [
        ((2020, 2050, 2080), "Anyville", "999999", 50.0, -124.5, 100.0),
        # ("Elsewhere", "11111", 51.1, -125.2, 1000.0),
    ],
)
def test_index_many_wx_files(
    years, city, code, lon, lat, elev, db_session, make_wx_file
):
    for year in years:
        wx_file_file_path = make_wx_file(year, city, code, lon, lat, elev)
        index_wx_file(db_session, "cmip5", wx_file_file_path)

    station_q = db_session.query(Location)
    assert station_q.count() == 1

    wx_file_q = db_session.query(WxFile)
    assert wx_file_q.count() == len(years)
