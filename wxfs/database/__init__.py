"""ORM for the Wx Files database.

"""
# TODO: Relationships
# TODO: Datetime of indexing? Do we care?

from sqlalchemy import (Column, DateTime, Enum, Integer, String, Numeric, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Station(Base):
    """A station is a location for which there are files."""
    __tablename__ = "stations"
    id = Column('station_id', Integer, primary_key=True, nullable=False)
    name = Column(String(256), nullable=False)
    code = Column(String(64), nullable=False)
    longitude = Column(Numeric, nullable=False)
    latitude = Column(Numeric, nullable=False)
    elevation = Column(Numeric, nullable=True)


class File(Base):
    """Base type for polymorphic file objects. """
    id = Column('file_id', Integer, primary_key=True, nullable=False)
    # Discriminator for polymorphic type
    fileType = Column(
        Enum("summary", "weather"),
        nullable=False
    )
    filepath = Column(String(2048), nullable=False)
    # Relationships
    station_id = Column(Integer, ForeignKey('stations.station_id'))


class SummaryFile(File):
    """A summary file contains a summary of weather data and context and explanatory
    information about that data.
    fileType == "summary"
    There are no additional attributes for this object.
    """
    pass


class WxFile(File):
    """A weather file contains weather information for a particular station.
    fileType == "weather"
    """
    creationDate = Column(DateTime, nullable=False)  # nullable?
    dataSource = Column(String(1024), nullable=False)
    designDataType = Column(
        Enum("TMY"),
        nullable=False
    )
    scenario = Column(
        Enum("RCP2.6", "RCP4.5", "RCP8.5"),
        nullable=False
    )
    timePeriod = Column(

    )
    ensembleStatistic = Column(
        Enum("average", "median", "10th percentile", "90th percentile"),
        nullable=False
    )



