from datetime import datetime


today = datetime.today().strftime("%Y-%m-%d")

fileId = 0
files = []


def makeFileCommon():
    global fileId
    fileId += 1
    return {
        "id": f"{fileId}",
        "selfUri": f"/files/{fileId}",
        "contentUri": f"/files/{fileId}/content",
    }


def makeWxFile(tStart, tEnd):
    file = {
        **makeFileCommon(),
        "fileType": "weather",
        "creationDate": today,
        "dataSource": "CWEC2016",
        "designDataType": "TMY",
        "scenario": "RCP8.5",
        "timePeriod": {
            "start": tStart,
            "end": tEnd,
        },
        "ensembleStatistic": "median",
        "variables": "all thermodynamic",
        "anomaly": "daily",
        "smoothing": "21",
    }
    files.append(file)
    return file


def makeSummaryFile():
    file = {
        **makeFileCommon(),
        "fileType": "summary",
        "scenario": "RCP8.5",
        "ensembleStatistic": "multiple",
        "timePeriod": "all",
        "variables": "all thermodynamic",
    }
    files.append(file)
    return file


locationId = -1
locations = []


def makeLocation(city, province, country, code, latitude, longitude, elevation):
    global locationId
    locationId += 1
    location = {
        "id": f"{locationId}",
        "selfUri": f"/locations/{locationId}",
        "city": city,
        "province": province,
        "country": country,
        "code": code,
        "latitude": latitude,
        "longitude": longitude,
        "elevation": elevation,
        "files": [
            makeWxFile("2010-01-01", "2039-12-31"),
            makeWxFile("2040-01-01", "2069-12-31"),
            makeWxFile("2070-01-01", "2099-12-31"),
            makeSummaryFile(),
        ],
    }
    locations.append(location)
    return location


makeLocation(
    "Abbotsford Intl AP",
    "BC",
    "CAN",
    "711080",
    49.02530,
    -122.3600,
    59.1,
),
makeLocation(
    "Agassiz",
    "BC",
    "CAN",
    "711130",
    49.24310,
    -121.7603,
    19.3,
),
makeLocation(
    "Blue River AP",
    "XX",
    "CAN",
    "718830",
    52.12910,
    -119.2895,
    682.8,
),
makeLocation(
    "Bonilla Island",
    "XX",
    "CAN",
    "714840",
    53.49280,
    -130.6390,
    12.5,
),
