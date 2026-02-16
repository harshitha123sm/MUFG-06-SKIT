# Residential Apartment Rental Portal

Full-stack mini project with:
- **Public/Resident app (Angular 20 + Tailwind CSS)** for browsing units, viewing amenities, creating booking requests, and checking booking status.
- **Admin portal (Angular 20)** for booking review and occupancy insights.
- **Backend API (Flask + PostgreSQL + JWT)** for authentication, booking workflow, and admin operations.
- **Docker Compose** setup for one-command local deployment.

## Repository Structure

- `frontend/` — Angular 20 app (resident + admin views)
- `backend/` — Flask REST API and data models
- `docker-compose.yml` — Orchestrates frontend, backend, and PostgreSQL

## Features

### Resident
- Register/login via JWT auth
- Browse available units and amenities
- Submit booking requests
- View personal booking status

### Admin
- View occupancy dashboard
- View all booking requests
- Approve/decline bookings and update mock payment status (API endpoint)

### Database entities
- `users`
- `towers`
- `units`
- `amenities`
- `bookings`
- `unit_amenity` (many-to-many map)

## Quick Start (Docker)

```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:4200
- Backend API: http://localhost:5000
- PostgreSQL: `localhost:5432`

## Seed Demo Data

After containers are running, seed sample admin/resident users, towers, amenities, and units:

```bash
curl -X POST http://localhost:5000/api/seed
```

## Demo Credentials

- **Admin**
  - Email: `admin@portal.local`
  - Password: `Admin@123`

- **Resident**
  - Email: `resident@portal.local`
  - Password: `Resident@123`

## Important API Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/units`
- `GET /api/amenities`
- `POST /api/bookings`
- `GET /api/bookings/me`
- `GET /api/admin/dashboard`
- `GET /api/admin/bookings`
- `PATCH /api/admin/bookings/<id>`

## Backend Local Run (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Set `DATABASE_URL` and `JWT_SECRET_KEY` as needed.

## Frontend Local Run (without Docker)

```bash
cd frontend
npm install
npm run start
```

## Notes

- This is a mini-project starter and can be extended with:
  - role-based route guards in Angular,
  - richer admin CRUD for towers/units/amenities,
  - lease management module,
  - uploadable tenant documents,
  - real payment gateway integration.
