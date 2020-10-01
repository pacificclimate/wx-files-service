from flask import url_for
from wxfs.database import WxFile, SummaryFile
from wxfs import get_app_session


def uri(file):
    return url_for('.wxfs_api_files_get', id=file.id)


def single_item_rep(file):
    """Return representation of a single file item."""
    rep_common = {
        "id": file.id,
        "selfUri": uri(file),
        "fileType": file.fileType,
        "filepath": file.filepath,
        "contentUri": "TBD",
    }
    if file.fileType == "weather":
        return {
            **rep_common,
            "creationDate": file.creationDate,
            "dataSource": file.dataSource,
            "designDataType": file.designDataType,
            "scenario": file.scenario,
            "timePeriod": {
                "start": file.timePeriodStart,
                "end": file.timePeriodEnd,
            },
            "ensembleStatistic": file.ensembleStatistic,
            "variables": file.variables,
            "anomaly": file.anomaly,
            "smoothing": file.smoothing,
        }
    elif file.fileType == "summary":
        return {
            **rep_common,
            # TODO: It is probably not right to fill these in statically.
            #  See TODO in ORM definition
            "scenario": "RCP8.5",
            "ensembleStatistic": "multiple",
            "timePeriod": "all",
            "variables": "all thermodynamic",
        }
    else:
        raise ValueError(f"Invalid file type: {file.fileType}")


def collection_item_rep(file):
    """Return representation of a file collection item.
    May conceivably be different than representation of a single a file.
    """
    return single_item_rep(file)


def collection_rep(files):
    """Return representation of files collection. """
    return [collection_item_rep(file) for file in files]


def listing():
    session = get_app_session()
    # TODO: Find out if there is a way to query on File only and
    #  extend appropriately according to discriminator
    wx_files = (
        session
            .query(WxFile)
            .order_by(WxFile.id.asc())
            .all()
    )
    summary_files = (
        session
            .query(SummaryFile)
            .order_by(SummaryFile.id.asc())
            .all()
    )
    return collection_rep(wx_files + summary_files)


def get(id):
    file = (
        get_app_session()
            .query(File)
            .filter_by(id=id)
            .one()
    )
    return single_item_rep(file)


def getContent():
    return {}
