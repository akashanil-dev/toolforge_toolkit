#!/usr/bin/env python3


import os


import jwt  # PyJWT — used only for exception type check in the home route

from flask import Flask, jsonify, redirect, request, send_from_directory

import configs.auth_config as auth_config
from services.auth_service import verify_jwt

from routes.auth import auth_bp
from dotenv import load_dotenv

# Load environment variables from .env (SSH key path, bastion host, DB creds).
load_dotenv()

from extensions import db, migrate
from routes.config import config_bp
from routes.webservice import webservice_bp
from routes.deploy import deploy_bp
from routes.tools import tools_bp



# ── Database configuration ─────────────────────────────────────────────
_DB_USER = os.environ.get("DEPLOYR_DB_USER", "")
_DB_PASS = os.environ.get("DEPLOYR_DB_PASS", "")
_DB_HOST = os.environ.get("DEPLOYR_DB_HOST", "127.0.0.1")
_DB_PORT = os.environ.get("DEPLOYR_DB_PORT", "3306")
_DB_NAME = os.environ.get("DEPLOYR_DB_NAME", "deployr")

# Serve the Deployr frontend from the same origin as the API (no CORS, single
# entry point). Static files (styles.css, app.js, data.js) resolve from "/".

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
app.secret_key = auth_config.FLASK_SECRET_KEY

# Flask-SQLAlchemy — MySQL via PyMySQL driver
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{_DB_USER}:{_DB_PASS}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}"
    "?charset=utf8mb4"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Bind extensions to the app
db.init_app(app)
migrate.init_app(app, db)

# Import models so Alembic/Flask-Migrate can detect them for autogenerate.
import models  # noqa: F401  (side-effect import — registers metadata)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(config_bp)
app.register_blueprint(webservice_bp)
app.register_blueprint(deploy_bp)
app.register_blueprint(tools_bp)


# ── CLI command: flask init-db ─────────────────────────────────────────
@app.cli.command("init-db")
def init_db_command():
    """Seed the database with default data (run after `flask db upgrade`)."""
    import db as _db
    import routes.tools as _tools_mod
    try:
        _db.init_db()
        _tools_mod.DB_OK = True
        print(f"[deployr] DB ready: {_db.DB_CONF['host']}:{_db.DB_CONF['port']}/{_db.DB_NAME}")
    except Exception as e:
        print(f"[deployr] init-db failed: {e}")


@app.route("/")
def index():
    """Home page — dashboard for authenticated users.

    Unauthenticated visitors are redirected to /login.
    """
    token = request.cookies.get("auth_token")
    if token:
        try:
            verify_jwt(token)
            return send_from_directory(FRONTEND, "index.html")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            # Invalid or expired token — clear stale cookie and redirect
            response = redirect("/login")
            response.delete_cookie("auth_token")
            return response

    return redirect("/login")


@app.route("/api")
def api_info():
    """API discovery banner."""
    return jsonify({
        "status": "ok",
        "message": "Toolforge Manager API is running",
        "endpoints": [
            {"path": "/api/tools", "methods": ["GET", "POST"]},
            {"path": "/api/tools/inspect", "methods": ["POST"]},
            {"path": "/api/tools/<id>", "methods": ["DELETE"]},
            {"path": "/api/config", "methods": ["GET", "POST"]},
            {"path": "/api/test-connection", "methods": ["POST"]},
            {"path": "/api/deploy", "methods": ["POST"]},
            {"path": "/api/webservice/status", "methods": ["POST"]},
            {"path": "/api/webservice/control", "methods": ["POST"]}
        ]
    })


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Toolforge Manager Backend App")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the Flask server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address to bind the Flask server to")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")

    args = parser.parse_args()

    with app.app_context():
        import db as _db
        import routes.tools as _tools_mod
        try:
            _db.init_db()
            _tools_mod.DB_OK = True
            print(f"[deployr] DB connected: {_db.DB_CONF['host']}:{_db.DB_CONF['port']}/{_db.DB_NAME}")
        except Exception as _db_err:
            _tools_mod.DB_OK = False
            print(f"[deployr] DB unavailable ({_db_err}); /api/tools will return empty.")

    print(f"Starting Toolforge Manager Backend Server on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
