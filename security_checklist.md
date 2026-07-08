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
| `POST /api/cart/merge/` | Y | N | N/A | Merges guest cart items into authenticated user cart on login |
| `PATCH /api/cart/items/<id>/` | N | N | Y (Data checked on int cast) | Updates cart quantity |
| `DELETE /api/cart/items/<id>/` | N | N | N/A | Deletes item |
| `POST /api/checkout/` | N | N (Should add) | Y (Handled via Cart DB consistency) | Guest/User checkout, stock modification |
| `GET /api/products/search/` | N | N | N/A | Quick predictive search results for dropdown |
| `GET /api/products/<slug>/recommendations/` | N | N | N/A | Cached product recommendations |
| `GET /api/auth/preferences/` | Y (Manual) | N | N/A | Returns default size, skin type, and phone. Missing permission class attribute. |
| `PATCH /api/auth/preferences/` | Y (Manual) | N | Y (field whitelist) | Updates user profile preferences. Missing permission class attribute. |
| `GET /api/wishlist/` | N (Session) | N | N/A | View customer or session wishlist items |
| `POST /api/wishlist/` | N (Session) | N | Y | Adds product to wishlist |
| `DELETE /api/wishlist/items/<pk>/` | N (Session) | N | N/A | Removes product from wishlist |
| `GET /api/recently-viewed/` | N (Session) | N | N/A | View customer/session recently viewed products |
| `POST /api/recently-viewed/` | N (Session) | N | Y | Log product view (fire-and-forget) |
| `GET /api/orders/` | Y (Manual) | N | N/A | List customer's order history. Missing permission class attribute. |
| `GET /api/orders/<order_number>/` | N (Session) | N | N/A | Track order status by order number |
| `POST /api/orders/items/<item_id>/return/` | Y (Manual) | N | Y | Request item return. Missing permission class attribute. |
| `GET /api/orders/admin/dashboard/` | Y (Admin) | N | N/A | Admin KPI stats dashboard |
| `GET /api/orders/admin/orders/` | Y (Admin) | N | N/A | Kanban dashboard orders list |
| `PATCH /api/orders/admin/orders/<pk>/status/` | Y (Admin) | N | Y | Update order status and append tracking |
| `GET /api/orders/admin/inventory/low-stock/` | Y (Admin) | N | Y | List inventory items under stock threshold |
| `GET /api/orders/admin/inventory/expiring/` | Y (Admin) | N | Y | List cosmetics close to expiration date |
| `GET /api/orders/admin/discounts/` | Y (Admin) | N | N/A | List discount rules |
| `POST /api/orders/admin/discounts/` | Y (Admin) | N | Y (`DiscountRuleSerializer`) | Create a new discount rule |
| `PATCH /api/orders/admin/discounts/<pk>/` | Y (Admin) | N | Y (`DiscountRuleSerializer`) | Update a discount rule |
| `DELETE /api/orders/admin/discounts/<pk>/` | Y (Admin) | N | N/A | Delete a discount rule |
| `GET /api/orders/admin/abandoned-carts/` | Y (Admin) | N | Y | Retrieve inactive carts and items |
| `GET /api/orders/admin/analytics/` | Y (Admin) | N | Y | Fetch detailed business analytics and trends |
| `GET /api/products/admin/list/` | Y (Admin) | N | N/A | List products and variant/image counts |
| `GET /api/products/admin/<product_id>/variants/` | Y (Admin) | N | N/A | Retrieve product variants |
| `POST /api/products/admin/<product_id>/variants/` | Y (Admin) | N | Y (`ProductVariantSerializer`) | Create product variant |
| `PATCH /api/products/admin/<product_id>/variants/` | Y (Admin) | N | Y (`ProductVariantSerializer` partial) | Update product variant |
| `DELETE /api/products/admin/<product_id>/variants/` | Y (Admin) | N | N/A | Delete product variant |
| `POST /api/products/admin/<product_id>/variants/bulk/` | Y (Admin) | N | Y (variant matrix array) | Bulk variant creation |
| `POST /api/products/admin/<product_id>/images/` | Y (Admin) | N | Y (`ProductImageSerializer` array) | Bulk image upload |
| `PATCH /api/products/admin/<product_id>/images/` | Y (Admin) | N | Y (image orders array) | Reorder product image display sequence |
| `GET /api/products/admin/reviews/` | Y (Admin) | N | N/A | List pending reviews |
| `PATCH /api/products/admin/reviews/<pk>/` | Y (Admin) | N | Y | Approve or reject a review |
| `GET /api/products/admin/collections/` | Y (Admin) | N | N/A | List collections |
| `POST /api/products/admin/collections/` | Y (Admin) | N | Y (`CollectionSerializer`) | Create a collection |
| `GET /api/products/admin/collections/<pk>/` | Y (Admin) | N | N/A | Get collection details |
| `PATCH /api/products/admin/collections/<pk>/` | Y (Admin) | N | Y (`CollectionSerializer` partial) | Edit a collection |
| `DELETE /api/products/admin/collections/<pk>/` | Y (Admin) | N | N/A | Delete a collection |

