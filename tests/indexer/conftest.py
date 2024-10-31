import os

import pytest
import testing.postgresql

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import wxfs.database


@pytest.fixture()
def make_wx_file(tmpdir):
    def make(year, city, code, lon, lat, elev, scenario = "RCP85", format = 1):
        if format == 1:
            p = tmpdir.join(f"{year}s_CAN_BC_{city}.{code}_CWEC2016.epw")
            p.write(
                f"""LOCATION,{city},BC,CAN,CWEC2016,{code},{lat},{lon},-8.0,{elev} | Morphed:TAS,RHS,DWPT,PS | File Version: 2.1 | Creation Date: 2020-06-23
OTHER STUFF
"""
            )
        elif format == 2:
            p = tmpdir.join(f"MORPHED_{scenario}_{year}s_CAN_BC_{city}.{code}_CWEC2016.epw")
            p.write(f"""LOCATION,{city},BC,CAN,CWEC2016,{code},{lat},{lon},-8.0,{elev}
COMMENTS 1, Future-shifted CWEC2020 EPW file for the {year} using projections from the {scenario} scenario.
COMMENTS 2, Future-shifted variables:TAS,RHS,DWPT,PS, File Version: 3.0, Creation Date: 2020-06-23
OTHER STUFF
""")
            
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
