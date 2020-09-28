from wxfs.fake_data import locations


def listing():
    return locations


def get(id=None):
    return locations[id]
