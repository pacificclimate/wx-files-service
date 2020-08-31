"""
This module contains the methods needed to build the indexer.

The indexer scrapes information from an existing set of weather files and adds them to
the Wx Files database. The model for the directory/files set up is taken directly from
the existing collection of weather files now at PCIC.
"""

# Goals: Allow re-indexing, adding new files to same directory, etc.

import os
import logging
import re

from wxfs.database import (Station, WxFile, SummaryFile)
from wxfs.indexer.file_parsing import get_wx_file_info
from wxfs.indexer.db_helpers import find_or_insert


# Set up logging

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# Useful constants

wx_file_extension = ".epw"
summary_file_extension = ".xslx"


# Indexing functions

def index_station_collection(sesh, filepath):
    """
    Index a collection of station subdirectories in directory `filepath`.

    :param sesh: SQLAlchemy session for a Wx Files database.
    :param filepath: Filepath to root directory.
    :return:
    """
    logger.info(f"Indexing station collection at {filepath}")
    for entry in os.scandir(filepath):
        if entry.is_dir():
            # Should this really yield?
            yield index_station(sesh, entry.path)


def index_station(sesh, filepath):
    """
    Index a single station, defined by the files in station directory at `filepath`.

    A directory is a station directory if it contains at least one file with extension
    ".epw".

    :param sesh: SQLAlchemy session for a Wx Files database.
    :param filepath: Filepath of a station directory.
    :return: list of Wx Files database file objects.
    """

    logger.info(f"Indexing station at {filepath}")

    # We assume there are few (relevant) files in each directory, so that accumulating
    # all their paths is no big deal.
    wx_filepaths = []
    summary_filepath = None
    for entry in os.scandir(filepath):
        path = entry.path
        name, extension = os.path.splitext(path)
        extension = extension.lower()
        if entry.is_file():
            if extension == wx_file_extension:
                logger.debug(f"Found wx file {path}")
                wx_filepaths.append(path)
            elif extension == summary_file_extension:
                logger.debug(f"Found summary file {path}")
                summary_filepath = path

    files = [index_wx_file(sesh, filepath) for filepath in wx_filepaths]

    if len(files) > 0:
        station = files[0].station
        if not all(file.station == station for file in files):
            # Does this need to be pre-checked before doing any database activities?
            logger.warning("Shit, stations aren't all the same.")
        if summary_filepath is not None:
            files.append(index_summary_file(sesh, station, summary_filepath))
    else:
        logger.info(f"{filepath} does not contain any weather files")

    return files


def index_wx_file(sesh, filepath):
    """Index a weather file into the database.

    A weather file contains all information necessary to determine both its station
    and its content metadata. If a matching Station is not found in the database,
    one is created. If a matching WxFile is not found in the database, one is created.

    :param sesh: SQLAlchemy session for a Wx Files database.
    :param filepath: Filepath of weather file to index.
    :return: WxFile ORM object
    """
    logger.info(f"Indexing weather file {filepath}")
    check_extension(filepath, ".epw")
    with open(filepath, "r") as file:
        station_info, wx_file_info = get_wx_file_info(file)
        station = find_or_insert(sesh, Station, station_info, {})
        wx_file = find_or_insert(
            sesh,
            WxFile,
            {
                "fileType": "weather",
                **wx_file_info,
                "station": station,
            },
            {
                "filepath": filepath,
            }
        )
        return wx_file


def index_summary_file(sesh, station, filepath):
    """Index a summary file into the database.

    A summary file does not contain enough information to determine its station,
    so one must be provided externally. Actually, this might not be true, depending
    on how reliable and unique the station code is. For now, we will determine
    station externally.

    Also, a summary file doesn't have any metadata we need to extract, so inserting
    it is simple. But see note above.
    """
    logger.info(f"Indexing summary file {filepath}")
    check_extension(filepath, ".xslx")
    summary_file = find_or_insert(
        sesh,
        SummaryFile,
        {
            "station": station,
        },
        {
            "filepath": filepath,
        }
    )
    return summary_file


def check_extension(filepath, extension):
    """Raise an error if filepath does not have specified extension."""
    name, ext = os.path.splitext(filepath)
    if ext != extension:
        raise ValueError(f"File {filepath} does not have extension '{extension}'.")

