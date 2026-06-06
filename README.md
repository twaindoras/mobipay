MobiPay — Mobile Money Payment API
A production-style mobile money REST API built with Python (Flask) and SQLite, inspired by M-PESA. Includes a full web dashboard for demonstration.
---
Features
User registration & login with 4-digit PIN
JWT-based authentication (24-hour tokens)
Wallet balance inquiry
Wallet top-up / deposit
Peer-to-peer money transfer with validation
Full transaction history with pagination
Single transaction lookup by ID
Web dashboard (dark-themed, fully functional)
Input validation & error handling throughout
---
Tech Stack
Layer	Technology
Backend	Python 3.x + Flask
Auth	PyJWT (JSON Web Tokens)
Database	SQLite (via sqlite3)
Frontend	Vanilla HTML/CSS/JS
API Style	RESTful JSON
---
Project Structure
```
mpesa-api/
├── app.py                    # Entry point, Flask app, routes registration
├── mpesa.db                  # SQLite database (auto-created on first run)
├── src/
│   ├── auth.py               # JWT token generation & auth middleware
│   ├── db.py                 # Database connection & schema init
│   └── routes/
│       ├── users.py          # POST /api/auth/register, POST /api/auth/login
│       ├── wallet.py         # GET /api/wallet/balance, POST /api/wallet/deposit
│       └── transactions.py   # POST /api/transactions/send, GET /api/transactions/history
└── public/
    └── index.html            # Web dashboard
```
---
Setup & Running
Prerequisites
Python 3.8+
pip
Install dependencies
```bash
pip install flask PyJWT
```
Run the server
```bash
python app.py
```
Server starts at: http://localhost:5000  
Dashboard at: http://localhost:5000
---
API Endpoints
Method	Endpoint	Auth Required	Description
POST	/api/auth/register	No	Register a new user
POST	/api/auth/login	No	Login and receive JWT token
GET	/api/wallet/balance	Yes	Get current wallet balance
POST	/api/wallet/deposit	Yes	Top up wallet
POST	/api/transactions/send	Yes	Transfer money to another user
GET	/api/transactions/history	Yes	List all transactions
GET	/api/transactions/:id	Yes	Get single transaction
GET	/api/health	No	API health check
---
Example Usage (curl)
Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Jane Wanjiru", "phone": "0712345678", "pin": "1234"}'
```
Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "0712345678", "pin": "1234"}'
```
Check Balance
```bash
curl http://localhost:5000/api/wallet/balance \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
Send Money
```bash
curl -X POST http://localhost:5000/api/transactions/send \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receiver_phone": "0722000001", "amount": 500, "description": "Lunch money"}'
```
Transaction History
```bash
curl "http://localhost:5000/api/transactions/history?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
---
Business Rules
Minimum transfer: KES 10
Maximum transfer per transaction: KES 70,000
Maximum deposit: KES 150,000
PIN must be exactly 4 digits
Phone must be a valid Kenyan number (07xx, 01xx, +254)
New accounts start with KES 1,000 demo balance
---
Security Notes
PINs are hashed with SHA-256 before storage (upgrade to bcrypt in production)
JWT tokens expire after 24 hours
Change `JWT_SECRET` environment variable in production
Use PostgreSQL instead of SQLite for production deployments
Add HTTPS (TLS) in production — never serve financial APIs over plain HTTP
---
What to mention in interviews
Why Flask? Lightweight, easy to read, widely used in Kenyan startups
Why SQLite? Zero-config for development; swap to PostgreSQL with one line change
JWT vs sessions? JWTs are stateless — easier to scale horizontally
What would you add? Rate limiting, SMS notifications (Africa's Talking), transaction PIN confirmation, admin dashboard
---
Built as a portfolio project for CS industrial attachment applications.
