"""
This module contains the methods needed to build the indexer.

The indexer scrapes information from an existing set of weather files and adds them to
the Wx Files database. The model for the directory/files set up is taken directly from
the existing collection of weather files now at PCIC.
"""

# Goals: Allow re-indexing, adding new files to same directory, etc.

import os
import logging

from wxfs.database import Location, WxFile, SummaryFile, Version
from wxfs.indexer.file_parsing import get_wx_file_info, summarize_attribute
from wxfs.indexer.db_helpers import find_or_insert


# Set up logging

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# Useful constants

wx_file_extension = ".epw"
summary_file_extension = ".xlsx"


# Indexing functions


def index_location_collection(sesh, version, filepath):
    """
    Index a collection of location subdirectories in directory `filepath`.

    :param sesh: SQLAlchemy session for a Wx Files database.
    :param filepath: Filepath to root directory.
    :return:
    """
    logger.info(f"Indexing location collection at {filepath}")
    for entry in os.scandir(filepath):
        logger.debug(f"{entry} {entry.is_dir()} {entry.path}")
        if entry.is_dir():
            index_location(sesh, version, entry.path)


def index_location(sesh, version, filepath):
    """
    Index a single location, defined by the files in location directory at `filepath`.

    A directory is a location directory if it contains at least one file with extension
    ".epw".

    :param sesh: SQLAlchemy session for a Wx Files database.
    :param filepath: Filepath of a location directory.
    :return: list of Wx Files database file objects.
    """

    logger.info(f"Indexing location at {filepath}")

    # We assume there are few (relevant) files in each directory, so that accumulating
    # all their paths is no big deal.
    wx_filepaths = []
    summary_filepath = None
    for entry in os.scandir(filepath):
        path = entry.path
        name, extension = os.path.splitext(path)
        extension = extension.lower()
        if entry.is_file():
            logger.debug("It's a file")
            if extension == wx_file_extension:
                logger.debug(f"Found wx file {path}")
                wx_filepaths.append(path)
            elif extension == summary_file_extension:
                logger.debug(f"Found summary file {path}")
                summary_filepath = path
            else:
                logger.debug(f"Found unknown type of file {path}")

    files = [index_wx_file(sesh, version, filepath) for filepath in wx_filepaths]

    # index_wx_file() can return None if it skips a file. Filter these
    # from the results lest the following loops crash and burn
    skipped = [filepath for x, filepath in zip(files, wx_filepaths) if x is None]
    logger.info(
        "The following files were not indexed for a variety of reasons: %s",
        skipped,
    )
    logger.info("See logs above for details.")

    files = [x for x in files if x is not None]

    if len(files) > 0:
        location = files[0].location
        scenario = summarize_attribute(files, "scenario")

        if not all(file.location == location for file in files):
            # Does this need to be pre-checked before doing any database activities?
            logger.warning("Shit, locations aren't all the same.")
        if summary_filepath is not None:
            files.append(
                index_summary_file(sesh, location, scenario, version, summary_filepath)
            )
    else:
        logger.info(f"{filepath} does not contain any recognized files")

    return files


def index_wx_file(sesh, version, filepath):
    """Index a weather file into the database.

    A weather file contains all information necessary to determine both its location
    and its content metadata. If a matching Location is not found in the database,
    one is created. If a matching WxFile is not found in the database, one is created.

    :param sesh: SQLAlchemy session for a Wx Files database.
    :param filepath: Filepath of weather file to index.
    :return: WxFile ORM object
    """
    logger.info(f"Indexing weather file {filepath}")
    check_extension(filepath, wx_file_extension)
    with open(filepath, "r") as file:
        location_info, wx_file_info = get_wx_file_info(file)
        if location_info is None or wx_file_info is None:
            logger.info(f"Weather file {filepath} could not be processed, skipping")
            return None
        location = find_or_insert(sesh, Location, location_info, {})
        ver = find_or_insert(sesh, Version, {"name": version}, {})
        wx_file = find_or_insert(
            sesh,
            WxFile,
            {
                "fileType": "weather",
                **wx_file_info,
                "location": location,
                "version": ver,
            },
            {"filepath": filepath},
        )
        return wx_file


def index_summary_file(sesh, location, scenario, version, filepath):
    """Index a summary file into the database.

    A summary file does not contain enough information to determine its location,
    so one must be provided externally. Actually, this might not be true, depending
    on how reliable and unique the location code is. For now, we will determine
    location externally.

    Also, a summary file doesn't have any metadata we need to extract, so inserting
    it is simple. But see note above.
    """
    logger.info(f"Indexing summary file {filepath}")
    check_extension(filepath, summary_file_extension)

    ver = find_or_insert(sesh, Version, {"name": version}, {})
    summary_file = find_or_insert(
        sesh,
        SummaryFile,
        {
            "fileType": "summary",
            "location": location,
            "version": ver,
            "scenario": scenario,
        },
        {"filepath": filepath},
    )
    return summary_file


def check_extension(filepath, extension):
    """Raise an error if filepath does not have specified extension."""
    name, ext = os.path.splitext(filepath)
    if ext != extension:
        raise ValueError(f"File {filepath} does not have extension '{extension}'.")
