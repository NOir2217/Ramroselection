# Security Checklist

This document tracks security and infrastructure hardening across the project. 

## Phase 0 Foundations

- [x] JWT Auth: Access token returned in body, short-lived (15 mins)
- [x] JWT Auth: Refresh token in httpOnly, Secure, SameSite=Strict cookie
- [x] JWT Auth: Token rotation and blacklist enabled on refresh/logout
- [x] Environment Separation: `settings/dev.py` and `settings/production.py` created
- [x] Secrets Management: `.env` file created (not committed) using `python-decouple`
- [x] HTTPS Enforcement: `SECURE_SSL_REDIRECT = True`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True` in production
- [x] CORS configuration: `CORS_ALLOW_ALL_ORIGINS = False` in production, strict whitelist used
- [x] CSRF Protection: Django defaults kept intact
- [x] Password Storage: Default Django PBKDF2/Argon2
- [x] Rate Limiting: `django-ratelimit` applied to login/register (5/min per IP)
- [x] Input Validation: DRF Serializers used on all endpoints
- [x] SQL Injection: Django ORM parameterization used exclusively
- [x] Security Headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` enabled
- [x] Custom Admin URL: Django admin moved to `/ramro-admin/`
- [ ] Dependency Hygiene: `pip list --outdated` and `npm audit` run before launch

> **Note on Database**: SQLite is currently used for development. Before real customer traffic, this must be migrated to PostgreSQL, as SQLite does not handle concurrent writes well at scale.

## API Endpoint Security Matrix

| Endpoint | Auth Required | Rate Limited | Input Validated via Serializer | Notes |
|---|---|---|---|---|
| `POST /api/auth/register/` | N | Y (5/min) | Y (`RegisterSerializer`) | Creates User & Profile, sets refresh cookie |
| `POST /api/auth/token/` | N | Y (5/min) | Y | Login endpoint, sets refresh cookie |
| `POST /api/auth/token/refresh/` | N | N | Y | Reads httpOnly cookie, rotates refresh token |
| `POST /api/auth/token/logout/` | Y | N | N/A | Blacklists token, clears cookie |
| `GET /api/products/` | N | N | N/A | Paginated list of products, read-only |
| `GET /api/products/<slug>/` | N | N | N/A | Full product details |
| `GET /api/cart/` | N | N | N/A | Reads cart_token cookie for guest, returns cart |
| `POST /api/cart/items/` | N | N | Y (`CartItemSerializer` - implicit via object creation) | Adds to cart, creates cookie if guest |
| `PATCH /api/cart/items/<id>/` | N | N | Y (Data checked on int cast) | Updates cart quantity |
| `DELETE /api/cart/items/<id>/` | N | N | N/A | Deletes item |
| `POST /api/checkout/` | N | N (Should add) | Y (Handled via Cart DB consistency) | Guest/User checkout, stock modification |
