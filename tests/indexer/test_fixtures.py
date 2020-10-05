import pytest


@pytest.mark.parametrize(
    "year, city, code, lon, lat, elev",
    [
        (2020, "Anyville", 999999, 50.0, -124.5, 100.0),
    ],
)
def test_make_wx_file(year, city, code, lon, lat, elev, make_wx_file):
    with open(make_wx_file(year, city, code, lon, lat, elev), "r") as wx_file:
        print("\n", wx_file.name)
        print(wx_file.readline())
        assert str(year) in wx_file.name
