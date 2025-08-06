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
    """Return a list of all locations.
    
    Due to the potentially large number of locations, this function
    memoizes the result after the first call to avoid repeated database queries.

    TODO: Alternative strategies for caching may be preferable when more can be devoted to this app.
    """
    if locations_memo is not None:
        return locations_memo 
    else:
        locations = get_app_session().query(Location).order_by(Location.id.asc()).all()
        locations_memo = collection_rep(locations)
        return locations_memo


def get(id=None):
    location = get_app_session().query(Location).filter_by(id=id).one()
    return single_item_rep(location)

listing()  # Populate the memo on first access