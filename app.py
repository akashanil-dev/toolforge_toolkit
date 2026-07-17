#!/usr/bin/env python3


import os

import jwt  # PyJWT — used only for exception type check in the home route

from flask import Flask, jsonify, redirect, request, send_from_directory

import configs.auth_config as auth_config
from services.auth_service import verify_jwt

from routes.auth import auth_bp
from routes.config import config_bp
from routes.webservice import webservice_bp
from routes.deploy import deploy_bp
from routes.tools import tools_bp


# Serve the Deployr frontend from the same origin as the API (no CORS, single
# entry point). Static files (styles.css, app.js, data.js) resolve from "/".
FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app = Flask(__name__, static_folder=FRONTEND, static_url_path="")
app.secret_key = auth_config.FLASK_SECRET_KEY

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(config_bp)
app.register_blueprint(webservice_bp)
app.register_blueprint(deploy_bp)
app.register_blueprint(tools_bp)

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
            {"path": "/api/webservice/status", "methods": ["GET"]},
            {"path": "/api/webservice/control", "methods": ["POST"]}
        ]
    })


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deployr — Toolforge Manager Backend")
    parser.add_argument("--port",  type=int, default=5000,       help="Port to listen on")
    parser.add_argument("--host",  type=str, default="127.0.0.1", help="Host address to bind")
    parser.add_argument("--debug", action="store_true",           help="Enable Flask debug mode")
    args = parser.parse_args()

    print(f"Starting Deployr on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
