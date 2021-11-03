from argparse import ArgumentParser
import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wxfs.fake_data import locations as locations_data
from wxfs.database import Base, Location, WxFile, SummaryFile
from wxfs.indexer.db_helpers import find_or_insert


def dict_subset(d, keys):
    if type(keys) == str:
        keys = re.split(r"\s*,\s*", keys)
    return {key: d[key] for key in keys if key in d}


def parse_time(s):
    return datetime.strptime(s, "%Y-%m-%d")


def create_database(engine):
    Base.metadata.create_all(bind=engine)


def populate(session):
    for location_data in locations_data:
        location = find_or_insert(
            session,
            Location,
            dict_subset(
                location_data,
                "city, province, country, code, longitude, latitude, elevation",
            ),
            {},
        )
        for file_data in location_data["files"]:
            if file_data["fileType"] == "weather":
                find_or_insert(
                    session,
                    WxFile,
                    {
                        **dict_subset(
                            file_data,
                            "fileType, dataSource, designDataType, "
                            "scenario, ensembleStatistic, "
                            "variables, anomaly, smoothing",
                        ),
                        "creationDate": parse_time(file_data["creationDate"]),
                        "timePeriodStart": parse_time(file_data["timePeriod"]["start"]),
                        "timePeriodEnd": parse_time(file_data["timePeriod"]["end"]),
                        "location": location,
                    },
                    {
                        "filepath": "filepath",
                    },
                )
            elif file_data["fileType"] == "summary":
                find_or_insert(
                    session,
                    SummaryFile,
                    {
                        "fileType": "summary",
                        "location": location,
                    },
                    {
                        "filepath": "filepath",
                    },
                )

    session.commit()


def main(dsn, actions):
    """
    Create a wxfs database and/or populate with some stuff.

    :param dsn: connection info for the modelmeta database to update
    :param actions: List of actions... Can be "create", "populate", or a list of both
    """
    engine = create_engine(dsn)

    engine.execute("SET search_path = wxfs, public")

    if "create" in actions:
        create_database(engine)

    if "populate" in actions:
        Session = sessionmaker(bind=engine)
        session = Session()
        populate(session)
        session.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--dsn",
        help="database connection string of the form "
        "postgresql://user:password@host:port/database",
        required=True,
    )
    parser.add_argument(
        "actions",
        choices=["create", "populate"],
        default=[],
        nargs="+",
        help="Create all of the necessary tables (not the database proper) for this"
        "application and/or populate said tables with some fake data for a"
        "sample deployment. Invocation can take of the form of neither, either"
        'or both choice. E.g. "database.py -d postgresql://user@host:port/database create populate"',
    )
    args = parser.parse_args()

    main(dsn=args.dsn, actions=args.actions)
