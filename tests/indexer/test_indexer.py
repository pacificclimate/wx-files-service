import pytest

import datetime

from wxfs.indexer import (index_wx_file)
from wxfs.database import (Station, WxFile)


@pytest.mark.parametrize("year, city, code, lon, lat, elev", [
    (2020, "Anyville", "999999", 50.0, -124.5, 100.0),
    (2050, "Elsewhere", "11111", 51.1, -125.2, 1000.0),
])
def test_index_one_wx_file(
    year, city, code, lon, lat, elev,
    db_session, make_wx_file
):
    wx_file_file_path = make_wx_file(year, city, code, lon, lat, elev)
    index_wx_file(db_session, wx_file_file_path)

    station = db_session.query(Station).one()
    assert station.name == f"{city},BC,CAN"
    assert station.code == code
    assert float(station.longitude) == lon
    assert float(station.latitude) == lat
    assert float(station.elevation) == elev

    wx_file = db_session.query(WxFile).one()
    assert wx_file.station == station
    assert wx_file.creationDate == datetime.datetime(2020, 6, 23)
    assert wx_file.dataSource == "CWEC2016"
    assert wx_file.designDataType == "TMY"
    assert wx_file.scenario == "RCP8.5"
    assert float(wx_file.timePeriodCentre) == year + 5;
    assert wx_file.ensembleStatistic == "average"


@pytest.mark.parametrize("years, city, code, lon, lat, elev", [
    ((2020, 2050, 2080), "Anyville", "999999", 50.0, -124.5, 100.0),
    # ("Elsewhere", "11111", 51.1, -125.2, 1000.0),
])
def test_index_many_wx_files(
    years, city, code, lon, lat, elev,
    db_session, make_wx_file
):
    for year in years:
        wx_file_file_path = make_wx_file(year, city, code, lon, lat, elev)
        index_wx_file(db_session, wx_file_file_path)

    station_q = db_session.query(Station)
    assert station_q.count() == 1

    wx_file_q = db_session.query(WxFile)
    assert wx_file_q.count() == len(years)
