"""
Deployr — Central Auth Configuration

OAuth 2.0 endpoints, client credentials, JWT settings, and Flask secrets
for Wikimedia authentication.

Set credentials via environment variables or a local .env file at the
project root.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Wikimedia OAuth 2.0 Endpoints
# ---------------------------------------------------------------------------
OAUTH_AUTHORIZE_URL = "https://meta.wikimedia.org/w/rest.php/oauth2/authorize"
OAUTH_TOKEN_URL     = "https://meta.wikimedia.org/w/rest.php/oauth2/access_token"
OAUTH_PROFILE_URL   = "https://meta.wikimedia.org/w/rest.php/oauth2/resource/profile"

# ---------------------------------------------------------------------------
# OAuth Client Credentials
# Register at: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth2
# ---------------------------------------------------------------------------
OAUTH_CLIENT_ID     = os.environ["OAUTH_CLIENT_ID"]
OAUTH_CLIENT_SECRET = os.environ["OAUTH_CLIENT_SECRET"]

# ---------------------------------------------------------------------------
# Flask Configuration
# ---------------------------------------------------------------------------
FLASK_SECRET_KEY  = os.environ["FLASK_SECRET_KEY"]
OAUTH_REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:5000/callback")

# ---------------------------------------------------------------------------
# JWT Configuration
# ---------------------------------------------------------------------------
JWT_SECRET_KEY      = os.environ["JWT_SECRET_KEY"]
JWT_EXPIRATION_SECS = 3600  # 1 hour
