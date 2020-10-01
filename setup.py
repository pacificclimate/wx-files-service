import sys
from setuptools import setup, find_packages

__version__ = (0, 1, 0)

setup(
    name="wxfs",
    description="PCIC microservice for Wx Files (weather files)",
    keywords="sql database climate meteorology",
    packages=find_packages(),
    version=".".join(str(d) for d in __version__),
    url="http://www.pacificclimate.org/",
    author="Rod Glover",
    author_email="rglover@uvic.ca",
    install_requires=""" 
        python-dateutil
        Flask
        Flask-Cors
        Flask-SQLAlchemy
        connexion
        connexion[swagger-ui]
        alembic
        psycopg2
    """.split("\n"),
    zip_safe=True,
    include_package_data=True,
    tests_require=["pytest", "testing.postgresql"],
    scripts="""
        scripts/index_location
        scripts/index_location_collection
    """.split(),
    classifiers="""
        Development Status :: 2 - Pre-Alpha
        Environment :: Web Environment
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: GNU General Public License v3 (GPLv3)
        Operating System :: OS Independent
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3.7
        Topic :: Internet
        Topic :: Scientific/Engineering
        Topic :: Database
        Topic :: Software Development :: Libraries :: Python Modules
    """.split("\n")
)