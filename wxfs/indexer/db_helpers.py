"""Database utility functions for indexer"""

def find(sesh, Thing, attributes):
    """Find an existing database Thing matching the given attributes."""
    query = sesh.query(Thing).filter_by(**attributes)
    return query.first()


def insert(sesh, Thing, attributes):
    """Insert a new database Thing with given attributes."""
    thing = Thing(**attributes)
    sesh.add(thing)
    return thing


def find_or_insert(sesh, Thing, attributes):
    """Find or insert a database Thing with given attributes."""
    return find(sesh, Thing, attributes) or insert(sesh, Thing, attributes)
