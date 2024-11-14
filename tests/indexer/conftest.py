import os

import pytest
import testing.postgresql

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import wxfs.database


@pytest.fixture()
def make_wx_file(tmpdir):
    """WX Files may have their metadata specified in either of two formats, referred
    to here as "format 1" and "format 2". All files currently in the database
    are format 2, but format 1 is maintained in tests and code in case.
    Format 1 puts more metadata in the LOCATION line; format 2 spreads it across multiple
    COMMENTS lines.
    Separately to metadata format, some files specify the scenario in the filename and
    some don't. In order to test both options easily, Format 1 files are generated
    without the scenario in the filename, but format 2 files are generated with it."""

    def make(year, city, code, lon, lat, elev, scenario="RCP85", format=1):
        if format == 1:
            p = tmpdir.join(f"{year}s_CAN_BC_{city}.{code}_CWEC2016.epw")
            p.write(
                f"""LOCATION,{city},BC,CAN,CWEC2016,{code},{lat},{lon},-8.0,{elev} | Morphed:TAS,RHS,DWPT,PS | File Version: 2.1 | Creation Date: 2020-06-23
OTHER STUFF
"""
            )
        elif format == 2:
            p = tmpdir.join(
                f"MORPHED_{scenario}_{year}s_CAN_BC_{city}.{code}_CWEC2016.epw"
            )
            p.write(
                f"""LOCATION,{city},BC,CAN,CWEC2016,{code},{lat},{lon},-8.0,{elev}
COMMENTS 1, Future-shifted CWEC2020 EPW file for the {year} using projections from the {scenario} scenario.
COMMENTS 2, Future-shifted variables:TAS,RHS,DWPT,PS, File Version: 3.0, Creation Date: 2020-06-23
OTHER STUFF
"""
            )

        return os.path.join(p.dirname, p.basename)

    return make


@pytest.fixture()
def db_uri():
    with testing.postgresql.Postgresql() as pg:
        yield pg.url()


@pytest.fixture()
def db_engine(db_uri):
    engine = create_engine(db_uri)
    wxfs.database.Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture()
def db_session(db_engine):
    sesh = sessionmaker(bind=db_engine)()
    yield sesh
    sesh.rollback()
    sesh.close()
