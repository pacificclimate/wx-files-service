"""ORM for the Wx Files database.

"""
# TODO: Datetime of indexing? Do we care?

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Location(Base):
    """A location is a location for which there are files."""

    __tablename__ = "locations"
    id = Column("location_id", Integer, primary_key=True, nullable=False)
    city = Column(String(128), nullable=False)
    province = Column(String(2), nullable=False)
    country = Column(String(64), nullable=False)
    code = Column(String(64), nullable=False)
    longitude = Column(Numeric, nullable=False)
    latitude = Column(Numeric, nullable=False)
    elevation = Column(Numeric, nullable=True)


class Version(Base):
    """A version describes a ser of data files with a common history"""
    
    __tablename__ = "versions"
    id = Column("version_id", Integer, primary_key=True, nullable=False)
    name = Column(String(12), nullable=False)
    description = Column(String(64), nullable=True)


class File(Base):
    """Base type for polymorphic file objects."""

    __tablename__ = "files"
    id = Column("file_id", Integer, primary_key=True, nullable=False)
    # Discriminator for polymorphic type
    fileType = Column(
        Enum("summary", "weather", name="fileType"), nullable=False
    )
    filepath = Column(String(2048), nullable=False)
    
    scenario = Column(
        Enum("RCP26", "RCP45", "RCP85", 
             "SSP585", "SSP245", "SSP126", "multiple", 
             name="scenario"), 
        nullable=False
    )

    # Relationships
    location_id = Column(Integer, ForeignKey("locations.location_id"))
    version_id = Column(Integer, ForeignKey("versions.version_id"))

    __mapper_args__ = {
        "polymorphic_identity": "files",
        "polymorphic_on": fileType,
    }


class SummaryFile(File):
    """A summary file contains a summary of weather data and context and explanatory
    information about that data.
    fileType == "summary"
    There are no additional attributes for this object.
    """

    __tablename__ = "summary_files"
    id = Column(
        "summary_file_id",
        Integer,
        ForeignKey("files.file_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    # TODO: Add attributes scenario, ensembleStatistic(s), timePeriod(s), variables.
    #  These should be raised up to File where appropriate (variables, ...).

    # Relationships
    location = relationship("Location", backref="summary_files")
    version = relationship("Version", backref='summary_files')

    __mapper_args__ = {"polymorphic_identity": "summary"}


class WxFile(File):
    """A weather file contains weather information for a particular location.
    fileType == "weather"
    """

    __tablename__ = "wx_files"
    id = Column(
        "wx_file_id",
        Integer,
        ForeignKey("files.file_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    creationDate = Column(DateTime, nullable=False)  # nullable?
    dataSource = Column(String(1024), nullable=False)
    designDataType = Column(
        Enum("TMY", "XMY", "TSY", "AMY", "design day", name="designDataType"),
        nullable=False,
    )

    timePeriodStart = Column(DateTime, nullable=False)
    timePeriodEnd = Column(DateTime, nullable=False)
    ensembleStatistic = Column(
        Enum(
            "average",
            "median",
            "10th percentile",
            "90th percentile",
            name="ensembleStatistic",
        ),
        nullable=False,
    )
    variables = Column(String(65), nullable=False)
    anomaly = Column(
        Enum("daily", "seasonal", "annual", name="anomaly"), nullable=False
    )
    smoothing = Column(Integer, nullable=True)

    # Relationships
    location = relationship("Location", backref="wx_files")
    version = relationship("Version", backref="wx_files")

    __mapper_args__ = {"polymorphic_identity": "weather"}
