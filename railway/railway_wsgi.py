"""HomeHub's WSGI app behind Railway's proxy.

Railway's edge sends the visitor's address in X-Forwarded-For and the scheme in
X-Forwarded-Proto. Without ProxyFix every visitor shares the proxy's address, so five
wrong passwords from anyone would lock the login form for the whole household.
"""
import os

from werkzeug.middleware.proxy_fix import ProxyFix

from wsgi import app  # noqa: E402  (HomeHub's own wsgi.py in /app)

# Railway serves public domains over HTTPS only, so the session cookie can be Secure.
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('HOMEHUB_SECURE_COOKIE', '1') != '0'
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
