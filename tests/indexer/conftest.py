import os
import pytest


@pytest.fixture()
def make_wx_file(tmpdir):
    def make(year, city, code, lon, lat, elev):
        p = tmpdir.join(f"{year}s_CAN_BC_{city}.{code}_CWEC2016.epw")
        p.write(f"""LOCATION,{city},BC,CAN,CWEC2016,{code},{lat},{lon},-8.0,{elev} | Morphed:TAS,RHS,DWPT,PS | File Version: 2.1 | Creation Date: 2020-06-23
OTHER STUFF
""")
        return p.open()

    return make

