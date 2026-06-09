import os

import connexion
from flask import jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.pool import NullPool

# This is a nasty way to do this.
#
# But at least the clients of this module (are supposed to) use
# `get_app_session()` instead of importing these globals directly.
# It would be better to hide these globals inside a singleton class, but that
# would take more effort than I am willing to spend for an essentially isomorphic
# solution.
#
# Note: Clients (API functions) *must* use `get_app_session()`. If instead they
# import these globals directly, the tests fail because their values are
# captured by the test framework before they are set to a non-None value.

connexion_app = None
flask_app = None
app_db = None


def _build_engine_options() -> dict[str, object]:
    """Build SQLAlchemy engine options from environment variables."""
    if os.getenv("SQLALCHEMY_POOL_CLASS", "").lower() == "null":
        return {"poolclass": NullPool}

    options: dict[str, object] = {"pool_pre_ping": True}

    for env_var, key, cast in [
        ("SQLALCHEMY_POOL_SIZE", "pool_size", int),
        ("SQLALCHEMY_MAX_OVERFLOW", "max_overflow", int),
        ("SQLALCHEMY_POOL_TIMEOUT", "pool_timeout", float),
        ("SQLALCHEMY_POOL_RECYCLE", "pool_recycle", float),
    ]:
        val = os.getenv(env_var)
        if val is not None:
            options[key] = cast(val)

    return options


def create_app(config_override={}):
    global connexion_app, flask_app, app_db
    connexion_app = connexion.FlaskApp(__name__, specification_dir="openapi/")

    flask_app = connexion_app.app
    CORS(flask_app)

    flask_app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv("WXFS_DSN", ""),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_ENGINE_OPTIONS=_build_engine_options(),
    )
    flask_app.config.update(config_override)

    app_db = SQLAlchemy(flask_app)

    @flask_app.route("/readyz")
    def readyz():
        status = {"status": "ok"}
        http_status = 200
        if request.args.get("verbose", "").lower() in ("1", "true", "yes"):
            try:
                get_app_session().execute(text("SELECT 1"))
                status["db"] = "ok"
            except Exception as exc:
                status["status"] = "error"
                status["db"] = str(exc)
                http_status = 503

        response = jsonify(status)
        response.cache_control.no_store = True
        return response, http_status

    # Must establish database before adding API spec(s). API specs refer to
    # handlers (`operationId`), which in turn import the database.
    # If you try to add the API spec before the database is defined, then the
    # import fails. This is a consequence of this particular project structure,
    # but it is (otherwise) a nice one and worth imposing this little bit of
    # ordering during setup.

    connexion_app.add_api("api-spec.yaml")

    return connexion_app, flask_app, app_db


def get_app_db():
    return app_db


def get_app_session():
    return app_db.session
