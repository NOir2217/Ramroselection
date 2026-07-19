from .base import *

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Strict CORS for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# HTTPS and Cookie Security
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Browser Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'same-origin'

# JWT Refresh Cookie Settings
JWT_COOKIE_NAME = 'refresh_token'
JWT_COOKIE_SECURE = True # Must be true over HTTPS
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SAMESITE = 'Strict' # Prevent CSRF

# Optional: Set a strict CSP via django-csp or manual middleware here if needed
