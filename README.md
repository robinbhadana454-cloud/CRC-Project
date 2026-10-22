# 🚆 RailConnect — Railway Ticket Booking Backend

RailConnect is a railway ticket booking backend developed using Python, FastAPI, SQLModel, and SQLite. It connects passengers and railway administrators through REST APIs.

Passengers can register, log in, search trains, book tickets, receive a unique PNR, view their booking history, and cancel eligible tickets. Administrators can manage trains, stations, routes, timings, fares, and seat availability.

This project uses fictional railway data. It does not connect to IRCTC, and payments are simulated.

## ✨ Features

### 👤 1. User Authentication and Accounts
- User registration and login.
- Password hashing using bcrypt.
- JWT authentication using `python-jose`.
- Protected APIs for authenticated users.
- View personal profile and booking history.
- Forgot-password and reset-password functionality.
- Expiring, single-use password reset tokens.
- Logout with a documented token-handling strategy.
- Users can access only their own bookings.

### 🛠️ 2. Admin Management
- Add, update, and deactivate trains.
- Add and manage railway stations.
- Configure train routes and timings.
- Set ticket fares and seat availability.
- Restrict railway management APIs to authorized administrators.

### 🔎 3. Train Search
- Search by starting station, destination, and journey date.
- View train names, numbers, timings, and routes.
- Check ticket fares and available seats.
- Handle invalid routes and journeys without matching trains.

### 🎫 4. Ticket Booking
- Book tickets for a selected train and journey.
- Generate a unique PNR (Passenger Name Record).
- Display booking confirmation.
- View booking history.
- Cancel eligible tickets.
- Update seat availability after booking and cancellation.
- Prevent overbooking and repeated seat release.

### 🔐 5. Reliability and Security
- Persistent data storage using SQLite.
- Request validation using Pydantic and SQLModel.
- Database transactions for booking and cancellation.
- Appropriate HTTP status codes and error messages.
- Authentication and role-based authorization.
- Automated tests for successful and failed requests.

### 💳 6. Payment Simulation
- Simulated payment status.
- No real payment gateway or financial transactions.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Backend development |
| FastAPI | REST API framework |
| Uvicorn | Application server |
| SQLModel | Database models and ORM |
| SQLite | Database storage |
| Pydantic | Input validation |
| python-jose | JWT authentication |
| bcrypt | Password hashing |
| pydantic-settings | Environment configuration |
| HTTPX | API testing |
| pytest | Automated testing |

## 📁 Project Structure

The following is a suggested structure. Keep the filenames consistent with your actual project.

```text
railconnect/
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
├── tests/
│   ├── __init__.py
│   └── test_api.py
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
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites
- Python 3.11 or newer.
- Git.
- Visual Studio Code (recommended).

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

Create a file named `requirements.txt` containing:

```text
fastapi
uvicorn[standard]
sqlmodel
pydantic-settings
python-jose[cryptography]
bcrypt
email-validator
httpx
pytest
```

Install the packages:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
SECRET_KEY=replace_with_a_secure_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./railconnect.db
```

Use the variable names expected by your code. Generate a strong secret key and never upload the actual `.env` file to GitHub.

### Step 5: Run the Application

```bash
uvicorn app.main:app --reload
```

If your application uses the structure shown above, open the following URLs:

- **Swagger API documentation:** http://127.0.0.1:8000/docs
- **ReDoc documentation:** http://127.0.0.1:8000/redoc
- **Local server:** http://127.0.0.1:8000

The database should be initialized by your application's database setup code.

## 🔌 API Endpoints

The following table describes the suggested API design. Update endpoint paths to match the routes implemented in your project.

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/auth/register` | Register a user | Public |
| POST | `/auth/login` | Log in and receive a JWT | Public |
| POST | `/auth/logout` | Log out | Authenticated |
| POST | `/auth/forgot-password` | Request password reset | Public |
| POST | `/auth/reset-password` | Reset password | Valid reset token |
| GET | `/users/me` | View own profile | Authenticated |
| GET | `/users/me/bookings` | View own bookings | Authenticated |
| GET | `/trains/search` | Search trains | Public |
| GET | `/trains/{train_id}` | View train details | Public |
| POST | `/bookings` | Book a ticket | Authenticated |
| GET | `/bookings/{booking_id}` | View a booking | Owner/admin |
| POST | `/bookings/{booking_id}/cancel` | Cancel a booking | Owner/admin |
| POST | `/admin/trains` | Add a train | Admin |
| PATCH | `/admin/trains/{train_id}` | Update a train | Admin |
| DELETE | `/admin/trains/{train_id}` | Deactivate a train | Admin |
| POST | `/admin/stations` | Add a station | Admin |
| POST | `/admin/routes` | Configure a route | Admin |

## 🚉 Example Booking Workflow

1. An administrator adds a train from New Delhi to Kanpur.
2. A passenger registers and logs in.
3. The passenger searches for trains using the source station, destination station, and journey date.
4. The passenger checks the fare and available seats.
5. The passenger books a ticket.
6. The backend generates a unique PNR and returns the booking confirmation.
7. The passenger views their booking history.
8. The passenger cancels an eligible ticket.
9. The backend restores seat availability after successful cancellation.

### Example Booking Response

This is an illustrative example, not a response captured from the running application.

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

The backend should handle the following scenarios correctly:

- **No seats available:** Reject the booking with an appropriate error.
- **Concurrent booking requests:** Use transactions and atomic database updates to prevent overbooking.
- **Successful cancellation:** Restore the seat count exactly once.
- **Repeated cancellation:** Reject a second cancellation without releasing seats again.
- **Unauthorized access:** Prevent passengers from viewing or modifying other users' bookings.
- **Duplicate PNR:** Enforce PNR uniqueness through a database constraint.

SQLite serializes database writes, but correct transactions, constraints, and seat-update logic are still necessary. If individual seats are assigned, enforce uniqueness for a seat on a particular train journey.

## 🧪 Testing

Install testing dependencies if needed:

```bash
pip install pytest httpx
```

Run your automated tests:

```bash
pytest -v
```

Tests should cover:

- Successful user registration and login.
- Failed login with invalid credentials.
- Unauthorized access to protected endpoints.
- Password reset, expiration, and token reuse.
- Admin-only train management.
- Train search and seat availability.
- Successful ticket booking and PNR generation.
- Booking failure when no seats are available.
- Concurrent booking attempts.
- Successful cancellation and seat restoration.
- Prevention of repeated cancellation.
- Protection of users' private booking information.

Add your actual test results after running the tests.

## 📸 Screenshots of Real API Requests and Responses

Save screenshots of your own running application in the `screenshots/` directory. Use Swagger UI at `http://127.0.0.1:8000/docs` or another API client.

### 1. Signup

![Signup API request and response](screenshots/signup.png)

### 2. Login

![Login API request and response](screenshots/login.png)

### 3. Failed Login or Unauthorized Access

![Failed login or unauthorized access response](screenshots/unauthorized.png)

### 4. Forgot Password and Reset Password

![Password reset API results](screenshots/password_reset.png)

### 5. Admin Adding a Train

![Admin train creation request and response](screenshots/admin_add_train.png)

### 6. Train Search and Seat Availability

![Train search and available seats](screenshots/train_search.png)

### 7. Ticket Booking and PNR Generation

![Booking confirmation and PNR](screenshots/booking_pnr.png)

### 8. Viewing and Cancelling a Booking

![Booking cancellation request and response](screenshots/booking_cancellation.png)

### 9. Automated Tests

![Automated tests running successfully](screenshots/tests.png)

**Screenshot requirements:**
- Capture real API requests and responses from your own application.
- Save the images using the filenames above.
- Keep all images inside the `screenshots/` folder.
- Never show passwords, JWT tokens, reset tokens, or secret keys.
- Ensure all image files exist before submitting the project.

## 🚪 Logout and Token Handling

The logout implementation depends on the authentication strategy used:

- **Stateless JWT:** The client discards its access token. The token can remain valid until expiration.
- **Server-side revocation:** The server invalidates a token or token identifier and checks revocation when protected APIs are accessed.

Document the strategy actually implemented in this project. Do not claim token revocation unless it is supported by your code.

## 🔐 Security Considerations

- Store password hashes rather than plain-text passwords.
- Load secrets from environment variables.
- Require authentication for protected APIs.
- Enforce administrator authorization for railway management.
- Expire password reset tokens and allow each token to be used only once.
- Restrict booking access to the booking owner or an authorized administrator.
- Use database constraints and transactions for booking consistency.
- Exclude secrets, local databases, caches, and virtual environments from Git.
- Never commit passwords, JWT tokens, or reset tokens.

## 🚧 Limitations

- Uses fictional railway data.
- Does not integrate with IRCTC.
- Does not process real payments.
- Email delivery may be simulated.
- SQLite is used for development and demonstration purposes.

## 🔮 Future Enhancements

- Real email-based password recovery.
- Refresh tokens and token revocation.
- Coach and seat selection.
- Waiting lists and ticket status management.
- Real payment gateway integration.
- Email and SMS notifications.
- PostgreSQL support.
- Docker-based deployment and cloud hosting.

## 📤 GitHub Upload

Initialize Git if the project is not already a repository:

```bash
git init
git add .
git commit -m "Initial RailConnect project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/railconnect.git
git push -u origin main
```

If the remote already exists, inspect it with:

```bash
git remote -v
```

Do not add the same remote a second time. Ensure `.gitignore` excludes local environment files, virtual environments, cache folders, and database files.

After uploading, verify that your GitHub repository contains:

- `README.md`
- `requirements.txt`
- Application source code.
- Automated test files.
- The `screenshots/` directory with actual screenshots.
- `.gitignore`
- `.env.example` without real secrets.

## ✅ Final Submission Checklist

- [ ] My README contains screenshots of real API requests and responses.
- [ ] I have included `requirements.txt` and tests.
- [ ] I have included signup and login screenshots.
- [ ] I have included failed login or unauthorized access screenshots.
- [ ] I have included forgot-password and reset-password screenshots.
- [ ] I have included an admin adding a train screenshot.
- [ ] I have included train search and seat availability screenshots.
- [ ] I have included a booking confirmation and PNR screenshot.
- [ ] I have included booking history and cancellation screenshots.
- [ ] I have included a screenshot of automated tests running successfully.
- [ ] I have checked that screenshot links work in the README.
- [ ] I have verified that the documented endpoints match my actual code.
- [ ] I have excluded passwords, JWT tokens, reset tokens, and secrets from GitHub.
- [ ] I have uploaded the source code, README, requirements, tests, and screenshots.

**Final verification:** Run your application and tests, capture the real results, and check every item before marking the project complete.

## 👨‍💻 Author

**Name:** Your Name

**Project:** RailConnect — Railway Ticket Booking Backend

**GitHub:** https://github.com/YOUR-USERNAME

## 📄 License

This project is intended for educational and demonstration purposes. Add a license file if you choose to distribute it under specific license terms.

---

**RailConnect — Making railway ticket booking simple, secure, and reliable.** 🚆
