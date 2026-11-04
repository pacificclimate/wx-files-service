import pytest

import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from wxfs.indexer import index_location, index_wx_file
from wxfs.database import Location, SummaryFile, WxFile


@pytest.mark.parametrize(
    "year, city, code, lon, lat, elev",
    [
        (2020, "Anyville", "999999", 50.0, -124.5, 100.0),
        (2050, "Elsewhere", "11111", 51.1, -125.2, 1000.0),
    ],
)
@pytest.mark.parametrize("version", ["CMIP5", "CMIP6"])
def test_index_one_wx_file(
    year, city, code, lon, lat, elev, version, db_session, make_wx_file
):
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

    wx_file = db_session.query(WxFile).one()
    assert wx_file.location == location
    assert wx_file.creationDate == datetime.datetime(2020, 6, 23)
    assert wx_file.dataSource == "CWEC2016"
    assert wx_file.designDataType == "TMY"
    assert wx_file.scenario == "RCP 8.5"
    print("timePeriodStart", wx_file.timePeriodStart)
    assert wx_file.timePeriodStart.year == year - 10
    print("timePeriodEnd", wx_file.timePeriodEnd)
    assert wx_file.timePeriodEnd.year == year + 19
    assert wx_file.ensembleStatistic == "average"
    assert wx_file.version == version


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
        index_wx_file(db_session, "CMIP5", wx_file_file_path)

    station_q = db_session.query(Location)
    assert station_q.count() == 1

    wx_file_q = db_session.query(WxFile)
    assert wx_file_q.count() == len(years)


@pytest.fixture
def memory_session():
    """Exercise find_or_insert with stored objects and no database connection."""
    records = []
    session = Mock(spec=["query", "add"])
    session.add.side_effect = records.append

    def query(model):
        def filter_by(**attributes):
            return SimpleNamespace(
                first=lambda: next(
                    (
                        record
                        for record in records
                        if isinstance(record, model)
                        and all(
                            getattr(record, key) == value
                            for key, value in attributes.items()
                        )
                    ),
                    None,
                )
            )

        return SimpleNamespace(filter_by=filter_by)

    session.query.side_effect = query
    return session


@pytest.fixture
def ssp_summaries(tmp_path, make_wx_file):
    summaries = {}
    for suffix, scenario in [
        ("SSP126", "SSP1-2.6"),
        ("SSP245", "SSP2-4.5"),
        ("SSP585", "SSP5-8.5"),
    ]:
        make_wx_file(
            2050, "Anyville", "999999", 50.0, -124.5, 100.0,
            scenario=suffix, format=2,
        )
        path = tmp_path / f"summary_{suffix}.xlsx"
        path.touch()
        summaries[str(path)] = scenario
    return summaries


def test_indexes_three_ssp_summaries(tmp_path, memory_session, ssp_summaries):
    files = index_location(memory_session, "CMIP6", str(tmp_path))

    summaries = [file for file in files if isinstance(file, SummaryFile)]
    assert len(summaries) == 3
    assert {file.filepath: file.scenario for file in summaries} == ssp_summaries
    weather = [file for file in files if isinstance(file, WxFile)]
    assert len(weather) == 3
    assert all(file.location is weather[0].location for file in summaries)
    assert all(file.version == "CMIP6" for file in summaries)


@pytest.mark.parametrize(
    "scenarios, expected",
    [(["RCP85"], "RCP 8.5"), (["SSP126", "SSP585"], "multiple")],
)
def test_indexes_legacy_summary(
    tmp_path, memory_session, make_wx_file, scenarios, expected
):
    for scenario in scenarios:
        make_wx_file(
            2050, "Anyville", "999999", 50.0, -124.5, 100.0,
            scenario=scenario, format=2,
        )
    path = tmp_path / "summary.xlsx"
    path.touch()

    files = index_location(memory_session, "CMIP6", str(tmp_path))

    summaries = [file for file in files if isinstance(file, SummaryFile)]
    assert len(summaries) == 1
    assert summaries[0].filepath == str(path)
    assert summaries[0].scenario == expected


@pytest.mark.parametrize(
    "filenames",
    [
        ["summary_SSP999.xlsx"],
        ["summary_SSP126.xlsx", "summary_SSP999.xlsx"],
        ["summary_SSP126.xlsx", "summary.xlsx"],
        ["summary_one.xlsx", "summary_two.xlsx"],
    ],
)
def test_rejects_unrecognized_summary_scenarios(
    tmp_path, memory_session, make_wx_file, filenames
):
    for scenario in ["SSP126", "SSP585"]:
        make_wx_file(
            2050, "Anyville", "999999", 50.0, -124.5, 100.0,
            scenario=scenario, format=2,
        )
    for filename in filenames:
        (tmp_path / filename).touch()

    with pytest.raises(ValueError, match="Cannot determine scenario for summary file"):
        index_location(memory_session, "CMIP6", str(tmp_path))
