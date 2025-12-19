# TouristManagement API

Lightweight Django REST Framework API for managing tourist sites, hotels, bookings, reviews, and favorites.

## Quick Start

- Create a virtual environment and activate it (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Install dependencies:

```bash
pip install -r requirements.txt
```

- Apply migrations and create a superuser:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

- Run the development server:

```bash
python manage.py runserver
```

API root will be available at `http://127.0.0.1:8000/api/`.

## Important configuration

- This project uses a custom user model declared as `AUTH_USER_MODEL = 'api.User'` in `TouristManagement/settings.py`.
- `django-filter` is used for filtering support. Make sure it's installed (included in `requirements.txt`).

## Endpoints

Main endpoints (registered in `api/urls.py`):

- `GET /api/tourist-sites/` - list tourist sites (supports pagination, search, filtering, ordering)
- `GET /api/tourist-sites/{id}/` - retrieve a tourist site (includes nested `hotels` list)
- `GET /api/hotels/` - list hotels (supports pagination, search, filtering, ordering)
- `GET /api/hotels/{id}/` - retrieve a hotel
- `GET /api/users/` - list users
- `POST /api/user-registration/` - register a new user
- `POST /api/user-login/` - login (custom viewset endpoint)
- `GET /api/favorites/`, `POST /api/favorites/` - favorites
- `GET /api/reviews/`, `POST /api/reviews/` - reviews
- `GET /api/bookings/`, `POST /api/bookings/` - bookings (server computes `total_cost`)

Also: DRF session auth at `/api/api-auth/`.

## Pagination

- Global default uses `PageNumberPagination` with page size `10` (configured in `TouristManagement/settings.py`).
- A custom paginator is implemented at `api/pagination.py` (`CustomPageNumberPagination`) which allows the query parameter `page_size` and enforces `max_page_size = 100`.

Examples:

- `/api/hotels/?page=2&page_size=5`

## Search, Filtering, and Ordering

- `TouristSiteViewSet` supports:

  - `search` on `name`, `description`, `history`, `region_or_city` (use `?search=term`)
  - `filter` by `region_or_city` (use `?region_or_city=CityName`)
  - `ordering` on `name`, `created_at` (use `?ordering=created_at` or `?ordering=-created_at`)

- `HotelViewSet` supports:
  - `search` on `name`, `description`, `address`
  - `filter` on `tourist_site`, `price_per_night`, `availability`
  - `ordering` on `price_per_night`, `distance_from_site`

Examples:

```bash
# search hotels containing "beach"
curl "http://127.0.0.1:8000/api/hotels/?search=beach"

# filter hotels for a tourist_site id and only available ones
curl "http://127.0.0.1:8000/api/hotels/?tourist_site=3&availability=True"

# order tourist sites by newest
curl "http://127.0.0.1:8000/api/tourist-sites/?ordering=-created_at"
```

## Nested serializers

- `TouristSiteSerializer` includes a read-only nested `hotels` field (see `api/serializers.py`). When you GET a tourist site (list or detail) you'll receive nested hotel objects.

Sample tourist site JSON (abbreviated):

```json
{
  "id": 1,
  "name": "Old Castle",
  "region_or_city": "Prague",
  "hotels": [
    { "id": 10, "name": "Castle Inn", "price_per_night": "75.00" },
    { "id": 11, "name": "Riverside Hotel", "price_per_night": "120.00" }
  ]
}
```

## Booking cost calculation

- `Booking.total_cost` is automatically calculated on the server when a `Booking` is saved. Provide `user`, `hotel`, `check_in_date`, and `check_out_date` when creating a booking; the server multiplies `hotel.price_per_night` by the number of nights.
- `total_cost` is a read-only field in the serializer. The model validates that `check_out_date` is after `check_in_date` and will raise a `400`-ish error via DRF if invalid.

Example create booking (JSON):

```bash
curl -X POST "http://127.0.0.1:8000/api/bookings/" \
  -H "Content-Type: application/json" \
  -d '{"user": 1, "hotel": 10, "check_in_date": "2025-12-20", "check_out_date": "2025-12-23"}'
```

Response will include `total_cost` calculated by the server.

## Testing

- Run Django tests if present:

```bash
python manage.py test
```

## JWT Authentication (Simple JWT)

- The project supports JWT auth via `djangorestframework-simplejwt`.
- Obtain tokens:

```bash
# obtain access & refresh tokens
curl -X POST "http://127.0.0.1:8000/api/token/" -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"yourpassword"}'

# refresh access token
curl -X POST "http://127.0.0.1:8000/api/token/refresh/" -H "Content-Type: application/json" -d '{"refresh":"<refresh-token>"}'
```

- Use the access token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer <access-token>
```

Note: Simple JWT expects credentials matching your `AUTH_USER_MODEL` — this project authenticates users by `email` as the `USERNAME_FIELD`.

## Permissions & Role-based Access

- Authentication: endpoints that create or modify user-owned resources require authentication (JWT or session). Use the `Authorization: Bearer <access-token>` header.
- Roles:

  - **Admin**: users with `is_admin=True` (or Django `is_superuser`) can create/update/delete protected resources such as tourist sites and hotels, and can list all users, bookings, reviews, and favorites.
  - **Regular authenticated user**: can create bookings, reviews, and favorites; can view public resources (tourist sites, hotels); can only list/read their own bookings, reviews, and favorites.
  - **Anonymous**: read-only access to tourism listings (`tourist-sites`, `hotels`) and can register/login.

- Endpoint protection summary:
  - `tourist-sites/`, `hotels/`: public read; create/update/delete allowed only for admins.
  - `users/`: admin-only.
  - `user-registration/`, `user-login/`, `token/`, `token/refresh/`: open to anonymous.
  - `favorites/`, `reviews/`, `bookings/`: authenticated users only for create; non-admins only see their own objects; admins can see and manage all objects.

Examples:

```bash
# as a regular user, list your bookings
curl -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/api/bookings/"

# as admin, list all bookings
curl -H "Authorization: Bearer $ADMIN_TOKEN" "http://127.0.0.1:8000/api/bookings/"
```

If you want stricter access (e.g., only authenticated users can read tourist sites/hotels), I can update the viewsets' `permission_classes` accordingly.


