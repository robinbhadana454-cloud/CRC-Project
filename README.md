# 🚆 RailConnect — Railway Ticket Booking Backend

RailConnect is a railway ticket booking backend built using **Python, FastAPI, SQLModel, and SQLite**. It provides a platform where passengers can register, log in, search for trains, book tickets, receive a unique PNR, view their bookings, and cancel eligible tickets.

Railway administrators can manage trains, stations, routes, fares, timings, and seat availability through protected APIs.

This project uses fictional railway data and simulated payments. It does not connect to IRCTC or any real railway booking system.

## ✨ Features

### 1. User Authentication and Accounts
- User registration and login.
- Secure password hashing using bcrypt.
- JWT-based authentication using `python-jose`.
- Protected APIs for authenticated users.
- User profile management.
- Forgot-password and reset-password functionality.
- Expiring, single-use password reset tokens.
- Logout with the token-handling approach documented in the project.
- Users can access only their own profiles and bookings.

### 2. Admin Management
- Add, update, and deactivate trains.
- Manage railway stations and routes.
- Configure train timings, fares, and seat availability.
- Restrict railway data management to authorized administrators.

### 3. Train Search
- Search trains by starting station, destination, and journey date.
- View train numbers, names, routes, departure and arrival times.
- Check ticket fares and available seats.
- Handle invalid routes and journeys with no matching trains.

### 4. Ticket Booking
- Book tickets for a selected train and journey date.
- Generate a unique PNR (Passenger Name Record).
- View booking confirmation and booking history.
- Cancel eligible tickets.
- Restore seat availability after successful cancellation.
- Prevent double booking and repeated seat release.

### 5. Reliability and Security
- Persistent data storage using SQLite.
- Input validation using Pydantic and SQLModel.
- Database transactions for booking and cancellation.
- Appropriate HTTP status codes and error messages.
- Authentication and authorization for protected endpoints.
- Automated tests for successful and failed requests.

### 6. Payment Simulation
- Simulated payment status for ticket bookings.
- No real payment gateway or financial transactions.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Backend programming |
| FastAPI | REST API development |
| Uvicorn | ASGI server |
| SQLModel | Database models and ORM |
| SQLite | Database storage |
| Pydantic | Data validation |
| python-jose | JWT authentication |
| bcrypt | Password hashing |
| pydantic-settings | Environment-based configuration |
| HTTPX | API testing |
| pytest | Automated testing, if configured |

## 📁 Project Structure

The project may follow this structure. Adjust it to match your actual files and folders.

```text
railconnect/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── config.py
│   ├── dependencies.py
│   └── routers/
│       ├── __init__.py
│       ├── users.py
│       ├── trains.py
│       ├── bookings.py
│       └── admin.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── screenshots/
│   ├── signup.png
│   ├── login.png
│   ├── unauthorized.png
│   ├── password_reset.png
│   ├── admin_add_train.png
│   ├── train_search.png
│   ├── booking_pnr.png
│   ├── booking_cancellation.png
│   └── tests.png
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

Install the following tools before running the project:

- Python 3.11 or newer
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/railconnect.git
cd railconnect
```

Replace `YOUR-USERNAME` with your GitHub username.

### Step 2: Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a local `.env` file using `.env.example` as a reference.

Example configuration:

```env
SECRET_KEY=replace_with_a_secure_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./railconnect.db
```

Use the variable names expected by your application. Generate a strong secret key for local development, and never commit `.env` or real secrets to GitHub.

### Step 5: Run the Application

```bash
uvicorn app.main:app --reload
```

If the application starts successfully, open:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc
- **Local API:** http://127.0.0.1:8000

The SQLite database should be initialized according to your application's database setup.

## 🔌 Important API Endpoints

The exact endpoint paths depend on your implementation. The following is a suggested API design.

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Public |
| POST | `/auth/login` | Log in and obtain a JWT | Public |
| POST | `/auth/logout` | Log out | Authenticated |
| POST | `/auth/forgot-password` | Request a password reset | Public |
| POST | `/auth/reset-password` | Reset a password | Valid reset token |
| GET | `/users/me` | View the current user's profile | Authenticated |
| GET | `/users/me/bookings` | View personal bookings | Authenticated |
| GET | `/trains/search` | Search trains and availability | Public |
| GET | `/trains/{train_id}` | Get train details | Public |
| POST | `/bookings` | Create a ticket booking | Authenticated |
| GET | `/bookings/{booking_id}` | View a booking | Booking owner/admin |
| POST | `/bookings/{booking_id}/cancel` | Cancel an eligible booking | Booking owner/admin |
| POST | `/admin/trains` | Add a train | Admin |
| PATCH | `/admin/trains/{train_id}` | Update train details | Admin |
| DELETE | `/admin/trains/{train_id}` | Deactivate a train | Admin |
| POST | `/admin/stations` | Add a station | Admin |
| POST | `/admin/routes` | Configure a route | Admin |

**Note:** These are suggested endpoint paths, not a claim that every endpoint is already implemented. Update the table to reflect your actual FastAPI routes.

## 🚉 Example Booking Workflow

A typical passenger journey follows these steps:

1. The administrator adds a train from New Delhi to Kanpur.
2. The passenger registers and logs in.
3. The passenger searches for trains using the origin, destination, and journey date.
4. The passenger checks the fare and available seats.
5. The passenger books a ticket.
6. The backend generates a unique PNR and returns booking confirmation.
7. The passenger views their booking history.
8. The passenger cancels an eligible ticket.
9. The backend updates seat availability after successful cancellation.

### Example Booking Response

The following is an illustrative response. Actual field names and values depend on your implementation.

```json
{
  "message": "Ticket booked successfully",
  "pnr": "RC202610220001",
  "status": "CONFIRMED",
  "train_name": "Delhi Kanpur Express",
  "source": "New Delhi",
  "destination": "Kanpur Central",
  "fare": 750.0,
  "payment_status": "SIMULATED_SUCCESS"
}
```

## 🔒 Booking Concurrency and Seat Management

RailConnect is designed to handle important booking scenarios safely.

- **No seats available:** Reject the booking and return an appropriate error.
- **Concurrent booking attempts:** Use appropriate database transactions and atomic seat updates to prevent overbooking.
- **Successful cancellation:** Restore the seat count only once.
- **Repeated cancellation:** Reject the second cancellation without releasing seats again.
- **Unauthorized access:** Prevent passengers from viewing or modifying other users' bookings.
- **Duplicate PNR:** Enforce PNR uniqueness at the database level.

SQLite serializes database writes, but the implementation must still use correct transactions, constraints, and seat-update logic. If individual seats are assigned, enforce uniqueness for a seat on a particular train journey.

## 🧪 Running Tests

Install the test dependencies if they are not already listed in `requirements.txt`.

```bash
pip install pytest httpx
```

Run the automated tests:

```bash
pytest -v
```

The tests should cover:

- Successful registration and login.
- Failed login with invalid credentials.
- Unauthorized access to protected APIs.
- Password reset success, expiry, and reuse attempts.
- Admin-only train management.
- Train search and seat availability.
- Successful ticket booking and unique PNR generation.
- Booking failure when no seats are available.
- Concurrent booking attempts.
- Successful cancellation and seat restoration.
- Prevention of repeated cancellation.
- User access restrictions for booking history.

Record the actual test results in this README after running the tests.

## 📸 Screenshots and Proof of Execution

All screenshots should come from your own running application using Swagger UI, HTTPX, or another API client. Save them in the `screenshots/` directory.

### 1. User Signup and Login

![Signup and login](screenshots/signup.png)

![Login response](screenshots/login.png)

### 2. Failed Login or Unauthorized Access

![Unauthorized request](screenshots/unauthorized.png)

### 3. Forgot Password and Reset Password

![Password reset results](screenshots/password_reset.png)

Do not display reset tokens or credentials in screenshots.

### 4. Admin Adding a Train

![Admin adds a train](screenshots/admin_add_train.png)

### 5. Train Search and Seat Availability

![Train search results](screenshots/train_search.png)

### 6. Ticket Booking and PNR Generation

![Booking confirmation and PNR](screenshots/booking_pnr.png)

### 7. Viewing and Cancelling a Booking

![Booking cancellation](screenshots/booking_cancellation.png)

### 8. Automated Tests

![Automated test results](screenshots/tests.png)

**Important:** Replace these image paths with screenshots of actual results. Ensure that all referenced image files exist in the repository.

## 🔐 Security Considerations

- Passwords are stored as hashes, never as plain text.
- JWT secrets are loaded from environment variables.
- Protected APIs validate authentication and authorization.
- Password reset tokens expire and should be usable only once.
- Development password-reset tokens must not be exposed in production.
- Logout should be documented accurately. Stateless JWTs generally remain valid until expiry unless server-side revocation or another invalidation mechanism is implemented.
- User data is restricted to authorized users.
- Database transactions and constraints protect booking consistency.
- Never commit `.env`, database files containing personal data, passwords, JWTs, or reset tokens.

## 🚪 Logout Implementation

The logout behavior depends on the authentication strategy:

- **Stateless JWT:** The client discards its access token. The token may remain valid until expiry.
- **Server-side revocation:** The application invalidates a token or token identifier and checks revocation on protected requests.

Document the approach actually implemented in this project.

## 🚧 Limitations

- Uses fictional railway data.
- No IRCTC integration.
- No real payment processing.
- Email delivery may be simulated in development.
- SQLite is intended for this project's development and demonstration needs; a production deployment may require a database and concurrency strategy suited to higher traffic.

## 🔮 Future Improvements

- Email-based password recovery.
- Refresh tokens and improved token revocation.
- Seat and coach selection.
- Waiting lists and ticket status management.
- Real payment gateway integration.
- Email or SMS booking notifications.
- PostgreSQL support.
- Deployment using Docker and a cloud hosting service.

## 👨‍💻 Author

**Name:** Your Name

**Project:** RailConnect — Railway Ticket Booking Backend

**GitHub:** https://github.com/YOUR-USERNAME

## 📄 License

This project is intended for educational and demonstration purposes. Add a license such as MIT only if you choose to distribute the project under those terms.

---

**RailConnect — Making railway ticket booking simple, secure, and reliable.** 🚆
