from flask import url_for
from wxfs.database import Location
from wxfs import get_app_session
from wxfs.api.files import collection_rep as files_collection_rep

locations_memo = None

def uri(location):
    return url_for(".wxfs_api_locations_get", id=location.id)


def single_item_rep(location):
    """Return representation of a single location item."""
    return {
        "id": location.id,
        "selfUri": uri(location),
        "city": location.city,
        "province": location.province,
        "country": location.country,
        "code": location.code,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "elevation": location.elevation,
        "files": (
            files_collection_rep(location.wx_files)
            + files_collection_rep(location.summary_files)
        ),
    }


def collection_item_rep(location):
    """Return representation of a location collection item.
    May conceivably be different than representation of a single a location.
    """
    return single_item_rep(location)


def collection_rep(locations):
    """Return representation of locations collection."""
    return [collection_item_rep(location) for location in locations]


def listing():
    locations = get_app_session().query(Location).order_by(Location.id.asc()).all()

    return locations_memo if locations_memo is not None

    locations_memo = collection_rep(locations)
    return locations_memo;


def get(id=None):
    location = get_app_session().query(Location).filter_by(id=id).one()
    return single_item_rep(location)
