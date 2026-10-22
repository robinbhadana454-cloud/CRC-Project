# 🚆 RailConnect - Mini Railway Booking System Backend

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.22+-success.svg)](https://sqlmodel.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-26%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

> **The RailConnect Challenge Submission**  
> A production-grade, highly reliable mini railway booking platform backend built with **FastAPI**, **SQLModel**, **SQLite**, and **Pydantic**. Bridges passenger booking needs with administrative railway management, featuring atomic transactions, optimistic concurrency control to prevent overbooking, server-side JWT revocation, and single-use password recovery.

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Architecture & Reliability](#-architecture--reliability)
4. [Technology Stack](#-technology-stack)
5. [Installation & Setup](#-installation--setup)
6. [Running the Application](#-running-the-application)
7. [Running Tests](#-running-tests)
8. [API Endpoints Reference](#-api-endpoints-reference)
9. [Visual Proof & Screenshots](#-visual-proof--screenshots)
10. [Concurrency & Transaction Management](#-concurrency--transaction-management)
11. [Security Practices](#-security-practices)

---

## 🎯 Project Overview
RailConnect solves the core challenges of railway ticketing:
- **For Passengers**: Account creation, authenticated sessions, searching trains between stations by journey date, checking real-time available seats and fares, booking tickets, receiving unique 10-digit PNRs, viewing personal booking history, and cancelling tickets with automatic seat restoration and simulated refunds.
- **For Railway Administrators**: Secure access control, adding stations, configuring train schedules, route stops, departure/arrival timings, ticket fares, and setting seat inventories.
- **For System Integrity**: Prevents double-booking and race conditions when multiple passengers attempt to book the last remaining seat simultaneously. Protects against repeated ticket cancellations and unauthorized data access.

---

## ✨ Key Features

### 1. 🔐 Accounts & Authentication
- **Secure Registration & Login**: User registration with email validation and direct password hashing via `bcrypt`.
- **JWT Protection**: Signed JSON Web Tokens (HS256) via `python-jose` securing private passenger and administrative routes.
- **Server-Side Token Revocation (Logout)**: JWT `jti` denylisting in SQLite; logged-out tokens are immediately revoked.
- **Forgot & Reset Password**: Time-limited (15-min) single-use cryptographically secure reset tokens. Cannot be reused once consumed.
- **Privacy & Isolation**: Passengers can only view their own profile and booking records.

### 2. 🛠️ Administrative Control
- **Station Management**: Add and list railway stations with unique station codes (e.g., `NDLS`, `CNB`, `LKO`, `BCT`, `HWH`).
- **Train Management**: Add trains with source/destination stations, departure/arrival timings, total seat capacity, and base fares.
- **Route Stops & Schedules**: Configure intermediate stops with arrival/departure times, distance (km), and stage fares.
- **Train Deactivation**: Disable trains from search results and ticket booking.
- **Inventory Adjustments**: Directly set or adjust seat capacity and availability for specific journey dates.
- **System Oversight**: Inspect all passenger bookings across the railway network.

### 3. 🔍 Train Discovery & Seat Query
- **Route Search**: Find active trains connecting source and destination stations (direct or via route stops) on a specified journey date.
- **Real-Time Availability**: Inspect live available seats, departure/arrival times, travel duration, and fare.
- **Robust Validation**: Rejects past dates, identical source/destination queries, and non-existent station codes with clear error messages.

### 4. 🎟️ Ticketing, PNR & Cancellation
- **Atomic Booking**: Multi-passenger booking (up to 6 per ticket) in an atomic transaction.
- **Unique 10-Digit PNR**: Generates a guaranteed collision-free 10-character railway PNR.
- **Sequential Seat Allocation**: Assigns realistic seat numbers (`S-1`, `S-2`, ...) to passengers based on booked inventory.
- **Simulated Payment**: Automatically marks successful bookings as `PAID`.
- **Safe Cancellation & Restoration**: Cancels confirmed tickets, triggers simulated refund, and restores seat inventory. Prevents duplicate cancellations.

---

## 🏗️ Architecture & Reliability

```
fast-api/
│
├── app/
│   ├── config.py              # Configuration with pydantic-settings (.env support)
│   ├── database.py            # SQLModel engine, WAL mode, foreign keys, session dependency
│   ├── main.py                # FastAPI initialization, CORS, lifespan seeding, routing
│   │
│   ├── models/                # SQLModel database tables
│   │   ├── user.py            # User credentials, roles ("passenger" vs "admin"), active status
│   │   ├── station.py         # Station code, name, city, state
│   │   ├── train.py           # Train number, name, origin, destination, timings, fare, seats
│   │   ├── schedule.py        # Intermediate stops, stop sequence, arrival/departure, fare
│   │   ├── inventory.py       # Daily seat inventory with OCC versioning column
│   │   ├── booking.py         # Bookings, unique PNR, total fare, CONFIRMED/CANCELLED status
│   │   ├── passenger.py       # Passenger details and allocated seat numbers
│   │   └── token.py           # RevokedToken denylist and PasswordResetToken
│   │
│   ├── schemas/               # Pydantic v2 validation models & DTOs
│   │   ├── user.py            # UserRegister, UserLogin, TokenResponse, ResetPasswordRequest
│   │   ├── train.py           # TrainCreate, TrainUpdate, StationCreate, TrainResponse
│   │   ├── search.py          # TrainSearchResult, TrainSearchResponse, SeatAvailabilityResponse
│   │   └── booking.py         # BookingCreate, BookingResponse, CancelBookingResponse
│   │
│   ├── services/              # Business logic layer
│   │   ├── auth_service.py    # Registration, login, logout revocation, password reset
│   │   ├── train_service.py   # Admin operations for trains, stations, routes, and seats
│   │   ├── search_service.py  # Route discovery and lazy inventory initialization
│   │   ├── booking_service.py # Transactional booking, OCC concurrency, cancellation & refund
│   │   └── seed_service.py    # Database baseline seeder (admin, NDLS-CNB trains, inventory)
│   │
│   └── utils/                 # Security and helpers
│       ├── security.py        # bcrypt password hashing, JWT encode/decode, dependencies
│       └── pnr.py             # Unique 10-digit PNR generator
│
├── tests/                     # 26 automated pytest unit & integration tests
│   ├── conftest.py            # Test engine fixtures, isolated SQLite session, auth headers
│   ├── test_auth.py           # Auth, login, logout, password reset, unauthorized checks
│   ├── test_admin.py          # Admin endpoints, train creation, update, deactivation
│   ├── test_train_search.py   # Route search, invalid stations, past dates, empty routes
│   ├── test_booking.py        # Booking creation, PNR, seat decrement, cancel & restore
│   └── test_concurrency.py    # Optimistic locking race condition & double-booking prevention
│
├── scripts/
│   └── generate_screenshots.py# Live backend execution and screenshot capture
│
├── screenshots/               # Verified screenshots of running application
│   ├── 01_signup_and_login.png
│   ├── 02_failed_login_unauthorized.png
│   ├── 03_forgot_reset_password.png
│   ├── 04_admin_add_train.png
│   ├── 05_search_train_check_seats.png
│   ├── 06_booking_ticket_pnr.png
│   ├── 07_view_and_cancel_booking.png
│   └── 08_tests_running_successfully.png
│
├── requirements.txt           # Python dependencies
├── .env.example               # Template environment variables
└── README.md                  # Complete documentation
```

---

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Modern Python runtime |
| **FastAPI** | High-performance asynchronous web framework |
| **Uvicorn** | ASGI server for FastAPI |
| **SQLModel** | Unified ORM combining SQLAlchemy and Pydantic |
| **SQLite (with WAL & Foreign Keys)** | Lightweight, reliable relational database |
| **Pydantic v2 & Pydantic-Settings** | Strict data validation and environment settings management |
| **python-jose[cryptography]** | HS256 signed JSON Web Tokens (JWT) |
| **bcrypt** | Secure password hashing with unique salts |
| **pytest & httpx TestClient** | Automated test suite |

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/railconnect.git
cd railconnect
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration:
```ini
PROJECT_NAME="RailConnect Railway Booking Platform"
SECRET_KEY="super-secret-jwt-key-railconnect-2026-challenge-secure"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=120
RESET_TOKEN_EXPIRE_MINUTES=15
DATABASE_URL="sqlite:///./railconnect.db"
FIRST_SUPERUSER_EMAIL="admin@railconnect.com"
FIRST_SUPERUSER_PASSWORD="AdminSecret123!"
```

---

## 🏃 Running the Application

Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload
```

The application will automatically:
1. Initialize the SQLite database tables.
2. Enable SQLite `WAL` mode and `PRAGMA foreign_keys = ON`.
3. Seed the default administrator (`admin@railconnect.com` / `AdminSecret123!`).
4. Seed baseline stations (`NDLS`, `CNB`, `LKO`, `BCT`, `HWH`), sample trains, and seat inventories.

### Interactive API Documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Root Healthcheck**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧪 Running Tests

The test suite runs with **pytest** using isolated test databases:
```bash
python -m pytest -v
```

### Test Coverage Highlights:
- **26 Test Cases Passing** (100% success rate).
- **Authentication**: Registration, duplicate rejection, login, invalid passwords, unauthorized access, logout token revocation, forgot/reset password, and single-use token invalidation.
- **Admin Control**: Non-admin rejection (403), station creation, train creation, update, deactivation, and seat inventory overrides.
- **Train Discovery**: Route matching, invalid stations (404), past journey dates (400), same origin/destination (400), and non-existent routes.
- **Booking & Cancellation**: PNR generation, seat decrement, passenger seat assignment, cancellation and seat restoration, double cancellation rejection.
- **Concurrency**: Thread-pool race condition testing where concurrent bookings attempt to take the last available seat, verifying optimistic locking and zero overbooking.

---

## 📡 API Endpoints Reference

### 🔐 Authentication (`/api/v1/auth`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Public | Register a new passenger account |
| `POST` | `/api/v1/auth/login` | Public | Authenticate credentials and receive Bearer JWT |
| `POST` | `/api/v1/auth/logout` | Authenticated | Server-side token revocation / denylist |
| `POST` | `/api/v1/auth/forgot-password` | Public | Generate single-use expiring reset token |
| `POST` | `/api/v1/auth/reset-password` | Public | Reset password using valid reset token |
| `GET` | `/api/v1/auth/me` | Authenticated | View authenticated user profile |

### 🛠️ Admin Control (`/api/v1/admin`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/admin/stations` | Admin | Create a new railway station |
| `GET` | `/api/v1/admin/stations` | Admin | List all configured stations |
| `POST` | `/api/v1/admin/trains` | Admin | Add train with route stops, timings, fare, and seats |
| `PUT` | `/api/v1/admin/trains/{id}` | Admin | Update train timings, base fare, seats, or details |
| `PATCH` | `/api/v1/admin/trains/{id}/deactivate` | Admin | Deactivate train from search and booking |
| `POST` | `/api/v1/admin/inventory` | Admin | Manually update available seats for a journey date |
| `GET` | `/api/v1/admin/trains/{id}` | Admin | View comprehensive train configuration |
| `GET` | `/api/v1/admin/bookings` | Admin | View all bookings across entire system |

### 🔍 Train Discovery (`/api/v1/trains`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/v1/trains/search` | Public | Search trains by source, destination, and date |
| `GET` | `/api/v1/trains/stations` | Public | List all available stations for passengers |
| `GET` | `/api/v1/trains/{id}` | Public | Get specific train details and route stops |
| `GET` | `/api/v1/trains/{id}/availability` | Public | Query live available seats for a date |

### 🎟️ Bookings & Ticketing (`/api/v1/bookings`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/v1/bookings/` | Authenticated | Book tickets atomically and receive unique PNR |
| `GET` | `/api/v1/bookings/my-bookings` | Authenticated | View current passenger's booking history |
| `GET` | `/api/v1/bookings/{pnr}` | Authenticated | View specific booking details by PNR |
| `POST` | `/api/v1/bookings/{pnr}/cancel` | Authenticated | Cancel ticket, process refund, restore seats |

---

## 📸 Visual Proof & Screenshots

All screenshots below are captured directly from the **running backend application**. In strict compliance with security guidelines, all passwords, JWT tokens, and reset tokens are safely masked.

### 1. Signup and Login
New passenger account registration (`201 Created`) with bcrypt hashing and subsequent login (`200 OK`) returning a signed Bearer JWT token.
![Signup and Login](screenshots/01_signup_and_login.png)

---

### 2. Failed Login or Unauthorized Access
Demonstrating robust security controls: rejection of incorrect passwords (`401 Unauthorized`), rejection of missing Bearer tokens (`401 Unauthorized`), and blocking passenger access to admin APIs (`403 Forbidden`).
![Failed Login or Unauthorized Access](screenshots/02_failed_login_unauthorized.png)

---

### 3. Forgot-Password and Reset-Password Results
Simulated password recovery generating an expiring reset token, successful password update, and immediate rejection of attempted token reuse (`400 Bad Request`).
![Forgot and Reset Password](screenshots/03_forgot_reset_password.png)

---

### 4. Admin Adding a Train
Railway administrator registering Train 12004 (*Lucknow Swarna Shatabdi Express*) from New Delhi (`NDLS`) to Kanpur Central (`CNB`) with departure/arrival timings, intermediate route stops, base fare, and seat capacity.
![Admin Adding a Train](screenshots/04_admin_add_train.png)

---

### 5. Searching for a Train and Checking Seats
Passenger searches for trains connecting New Delhi to Kanpur for a journey date, viewing departure/arrival times, fare (Rs. 750.00), and confirming 60 available seats.
![Searching for a Train](screenshots/05_search_train_check_seats.png)

---

### 6. Booking a Ticket and Receiving a PNR
Passenger completes booking for 2 passengers. The system allocates seat numbers (`S-1`, `S-2`), sets payment status to `PAID`, and issues unique 10-digit PNR `8930016501`.
![Booking Ticket and Receiving PNR](screenshots/06_booking_ticket_pnr.png)

---

### 7. Viewing and Cancelling a Booking
Passenger inspects confirmed booking by PNR, executes ticket cancellation, receives simulated refund (Rs. 1500.00), and live query confirms seat availability is restored back to 60.
![Viewing and Cancelling a Booking](screenshots/07_view_and_cancel_booking.png)

---

### 8. Tests Running Successfully
All **26 automated test cases** running and passing with 100% success rate across authentication, admin, search, booking, concurrency, and route validation.
![Tests Running Successfully](screenshots/08_tests_running_successfully.png)

---

## ⚡ Concurrency & Transaction Management

### The Race Condition Challenge
What happens if only 1 seat is left on a train and two passengers attempt to book it at the exact same millisecond?

### RailConnect's Solution: Optimistic Concurrency Control (OCC)
1. **Versioned Seat Inventory**: Every `SeatInventory` record contains a `version` column.
2. **Conditional Atomic Update**: When booking seats, RailConnect executes an atomic SQL update statement:
   ```sql
   UPDATE seat_inventories
   SET available_seats = available_seats - :num_passengers,
       booked_seats = booked_seats + :num_passengers,
       version = version + 1,
       updated_at = :now
   WHERE id = :inv_id
     AND version = :current_version
     AND available_seats >= :num_passengers;
   ```
3. **Collision Detection**: If two transactions read `version = 1` concurrently:
   - Transaction A succeeds, increments `version` to 2, and commits.
   - Transaction B's `UPDATE` statement matches **0 rows** because `version` is no longer 1.
   - RailConnect detects `rowcount == 0`, rolls back the transaction, and returns `409 Conflict` (or `400 Bad Request` if seats are depleted), preventing overbooking.
4. **Idempotent Cancellation**: Cancellations check whether `status == "CANCELLED"`. Repeated cancellation requests are rejected, preventing repeated seat release.

---

## 🔒 Security Practices
- **Password Protection**: Passwords hashed using standard `bcrypt` with unique automatic salts. Plaintext passwords are never logged or stored.
- **Server-Side Token Revocation**: Logout actively records the token `jti` in a `revoked_tokens` database table with its expiration timestamp.
- **Single-Use Password Reset**: Reset tokens are random 32-byte cryptographically secure URL-safe tokens, expiring after 15 minutes, marked `is_used = True` upon consumption.
- **Data Isolation**: Database queries enforce ownership checks (`booking.user_id == current_user.id`), preventing unauthorized inspection of other passengers' itineraries.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
