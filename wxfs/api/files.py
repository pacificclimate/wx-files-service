from flask import url_for, send_file
from wxfs.database import File
from wxfs import get_app_session


def selfUri(file):
    return url_for(".wxfs_api_files_get", id=file.id)


def contentUri(file):
    return url_for(".wxfs_api_files_getContent", id=file.id)


def single_item_rep(file):
    """Return representation of a single file item."""
    rep_common = {
        "id": file.id,
        "selfUri": selfUri(file),
        "fileType": file.fileType,
        "filepath": file.filepath,
        "contentUri": contentUri(file),
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
            "scenario": file.scenario,
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
    """Return representation of files collection."""
    return [collection_item_rep(file) for file in files]


def listing():
    files = get_app_session().query(File).order_by(File.id.asc()).all()
    return collection_rep(files)


def get_file_by_id(id):
    return get_app_session().query(File).filter_by(id=id).one()


def get(id):
    file = get_file_by_id(id)
    return single_item_rep(file)


def getContent(id):
    file = get_file_by_id(id)
    return send_file(file.filepath, as_attachment=True)
