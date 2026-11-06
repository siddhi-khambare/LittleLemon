=========================================================================================
LITTLE LEMON RESTAURANT MANAGEMENT SYSTEM - API & CAPSTONE DOCUMENTATION
Coursera Meta Back-End Developer Capstone Project
=========================================================================================

1. PROJECT OVERVIEW
-------------------
Little Lemon is a family-owned Mediterranean restaurant based in Chicago.
This project is a full-featured web application and REST API system developed using:
- Python & Django 5+ / 6+
- Django REST Framework (DRF)
- MySQL Database (via mysqlclient)
- Token-based Authentication
- HTML5, CSS3, and JavaScript Fetch API

2. SYSTEM ARCHITECTURE & FILE STRUCTURE
---------------------------------------
LittleLemon/
├── manage.py                  # Django administrative utility
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (DB credentials, SECRET_KEY)
├── .gitignore                 # Prevents committing secrets & venv
├── Readme.txt                 # Project documentation
├── index.html                 # Frontend root (for Live Server & preview)
│
├── littlelemon/               # Project configuration
│   ├── settings.py            # App settings, MySQL config, REST_FRAMEWORK config
│   ├── urls.py                # Main URL routing (/api/, /restaurant/, /auth/)
│   ├── asgi.py                # ASGI application entrypoint
│   └── wsgi.py                # WSGI application entrypoint
│
├── restaurant/                # Core restaurant application
│   ├── models.py              # Menu and Booking data models
│   ├── serializers.py         # DRF serializers with input validations
│   ├── views.py               # API views (generics, ViewSets) and home template view
│   ├── urls.py                # App-level endpoints (/menu/, /booking/, /register/)
│   ├── tests.py               # Complete test suite (16 tests for models, APIs, auth)
│   ├── admin.py               # Django admin registration
│   └── migrations/            # Database schema migrations
│
├── templates/
│   └── index.html             # Little Lemon website template with reservation form
│
└── static/
    ├── style.css              # Official brand stylesheet (Playfair Display & Karla)
    └── Logo.svg               # Little Lemon vector logo

3. MYSQL DATABASE SETUP
-----------------------
Step 1: Open your MySQL CLI or MySQL Workbench and log in as root:
    mysql -u root -p

Step 2: Create the database:
    CREATE DATABASE littlelemon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

Step 3: Update your .env file with your local MySQL password:
    DB_NAME=littlelemon
    DB_USER=root
    DB_PASSWORD=<your_actual_mysql_password>
    DB_HOST=127.0.0.1
    DB_PORT=3306

Step 4: Run migrations to create tables in MySQL:
    python manage.py makemigrations
    python manage.py migrate

4. API ENDPOINTS SPECIFICATION
------------------------------

A. Menu Management Endpoints (/api/menu/):
------------------------------------------
- GET /api/menu/
  List all menu items.
  Response: 200 OK [ { "id": 1, "title": "Greek salad", "price": "12.99", "inventory": 20 }, ... ]

- POST /api/menu/
  Create a new menu item.
  Sample Payload (JSON):
  {
      "title": "Mediterranean Grilled Salmon",
      "price": "18.50",
      "inventory": 15
  }
  Response: 201 Created

- GET /api/menu/<id>/
  Retrieve single menu item by ID.
  Response: 200 OK

- PUT /api/menu/<id>/
  Update a menu item.
  Sample Payload (JSON):
  {
      "title": "Greek Salad Supreme",
      "price": "14.00",
      "inventory": 25
  }
  Response: 200 OK

- DELETE /api/menu/<id>/
  Delete a menu item.
  Response: 204 No Content

B. Table Booking Endpoints (/api/booking/):
-------------------------------------------
- GET /api/booking/
  List all table reservations (requires Token Authentication).
  Header: Authorization: Token <your_token>
  Response: 200 OK

- POST /api/booking/
  Create a reservation (allows guest bookings or automatically associates logged-in user).
  Sample Payload (JSON):
  {
      "name": "Rahul Sharma",
      "no_of_guests": 4,
      "booking_date": "2026-11-15T19:30:00Z"
  }
  Response: 201 Created

- GET /api/booking/<id>/
  Retrieve a specific booking (requires Authentication).
  Response: 200 OK

- PUT /api/booking/<id>/
  Update a reservation.
  Response: 200 OK

- DELETE /api/booking/<id>/
  Cancel/delete a reservation.
  Response: 204 No Content

C. Authentication Endpoints:
----------------------------
- POST /api/register/
  Register a new customer account (passwords are safely hashed via PBKDF2/Argon2).
  Sample Payload (JSON):
  {
      "username": "customer1",
      "email": "customer1@example.com",
      "password": "StrongPassword123!"
  }
  Response: 201 Created

- POST /api/api-token-auth/
  Obtain DRF authentication token (Login).
  Sample Payload (JSON):
  {
      "username": "customer1",
      "password": "StrongPassword123!"
  }
  Response: 200 OK { "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }

- POST /api/logout/
  Invalidate user token (Logout).
  Header: Authorization: Token <your_token>
  Response: 200 OK

5. COMMANDS TO RUN AND TEST
---------------------------
Activate Virtual Environment:
  .\littlelemon\venv\Scripts\Activate.ps1

Install Dependencies:
  pip install -r requirements.txt

Run Database Migrations:
  python manage.py migrate

Run Comprehensive Unit Tests (16 automated tests):
  python manage.py test

Start Django Server:
  python manage.py runserver

Access Web Application:
  http://127.0.0.1:8000/
=========================================================================================
