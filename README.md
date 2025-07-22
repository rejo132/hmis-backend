📄 Complete Resolved README.md - Easy to Copy
# Hospital Management Information System (HMIS) - Backend

A comprehensive Flask-based REST API for hospital management, including patient records, appointments, billing, inventory, and more.

## Features

- **User Management**: Multi-role authentication (Admin, Doctor, Nurse, Lab Tech, IT)
- **Patient Management**: Patient registration, medical records, and appointments
- **Medical Records**: Complete patient history, diagnoses, prescriptions, and vitals
- **Appointment System**: Schedule and manage patient appointments
- **Billing**: Invoice generation and payment tracking
- **Laboratory**: Lab orders, sample tracking, and results
- **Radiology**: Radiology orders and results management
- **Inventory**: Medical supplies and equipment management
- **Pharmacy**: Medication inventory and dispensing
- **Human Resources**: Staff scheduling, attendance, and payroll
- **Finance**: Expense tracking and reporting
- **Communication**: Internal messaging and notifications
- **Security**: Comprehensive audit logging and access controls

## Setup

### Quick Setup (Recommended)
Run the automated setup script:
```bash
chmod +x setup.sh
./setup.sh
Manual Setup
Clone the repository:
git clone https://github.com/<your-username>/hmis-backend.git
cd hmis-backend
Set up Python environment:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Configure environment: Create .env file in the root directory:
DATABASE_URL=sqlite:///hmis.db
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-secret-key
Run migrations:
export FLASK_APP=app.py
flask db upgrade
Seed database:
python seed.py
Run the app:
flask run
Test Users
After seeding, you can login with these test accounts:

Admin: username=admin, password=password123
Doctor: username=doctor1, password=password123
Nurse: username=nurse1, password=password123
IT: username=it1, password=password123
Lab Tech: username=labtech1, password=password123
API Documentation
Authentication
The API uses JWT tokens for authentication. Include the token in the Authorization header:

Authorization: Bearer <your-jwt-token>
Endpoints
Authentication
POST /api/login - User login
POST /api/register - User registration
Patient Management
GET /api/patients - List all patients
POST /api/patients - Create new patient
GET /api/patients/{id} - Get patient details
PUT /api/patients/{id} - Update patient
Medical Records
GET /api/records - List medical records
POST /api/records - Create new medical record
POST /api/vitals - Record patient vitals
Appointments
GET /api/appointments - List appointments
POST /api/appointments - Schedule appointment
Billing
GET /api/bills - List bills
POST /api/bills - Create bill
PUT /api/bills/{id} - Update bill status
POST /api/bills/refund - Process refund
POST /api/bills/claim - Submit insurance claim
Inventory & Pharmacy
GET /api/inventory - List inventory items
POST /api/inventory - Add inventory item
PUT /api/inventory/{id} - Update inventory
POST /api/inventory/dispense - Dispense medication
POST /api/medications - Create medication
Laboratory & Radiology
POST /api/lab-orders - Create lab order
POST /api/lab-samples - Record lab sample
POST /api/radiology-orders - Create radiology order
Asset & Bed Management
GET /api/assets - List equipment assets
POST /api/assets/maintenance - Schedule maintenance
GET /api/beds - List beds
POST /api/beds/reserve - Reserve bed
Finance & HR
GET /api/finance/expenses - List expenses
POST /api/finance/expenses - Create expense
GET /api/finance/payroll - List payroll
GET /api/employees - List employees
POST /api/employees - Create employee
Administration
GET /api/audit-logs - View audit logs
GET /api/security-logs - View security logs
GET /api/settings - Get system settings
GET /api/communication-settings - Get communication settings
Sample Requests
Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
Get Patients
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/patients
Record Vitals
curl -X POST http://localhost:5000/api/vitals \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": 1, "blood_pressure": "120/80", "temperature": 98.6, "pulse": 72, "respiration": 16}'
Configuration
Environment variables (set in .env):

SECRET_KEY - Flask secret key
JWT_SECRET_KEY - JWT signing key
DATABASE_URL - Database connection string (SQLite or PostgreSQL)
FLASK_ENV - Environment (development/production)
Database Setup
SQLite (Default)
The application uses SQLite by default for easy development setup.

PostgreSQL (Production)
For PostgreSQL setup, use the provided script:

chmod +x setup_postgresql.sh
./setup_postgresql.sh
Or manually configure:

DATABASE_URL=postgresql://username:password@localhost:5432/hmis_db
Production Deployment
Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
Using Docker
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
Database Schema
The application includes comprehensive database models for:

Users and Roles with RBAC
Patients and Emergency Contacts
Medical Records and Diagnoses
Appointments and Schedules
Billing and Payments
Inventory and Equipment
Laboratory and Radiology Orders
Vitals and Clinical Data
Audit Logs and Security
Communication and Notifications
Security Features
JWT-based authentication with configurable expiration
Role-based access control (RBAC)
Password hashing with Werkzeug security
Comprehensive audit logging
Error logging and monitoring
CORS support for frontend integration
Input validation and sanitization
Development
Running Tests
pytest tests/
Database Migrations
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
API Testing
The application is configured with CORS to allow frontend connections from http://localhost:3000.

Role-Based Access Control
| Endpoint | Admin | Doctor | Nurse | IT | Lab Tech | Pharmacist | |----------|-------|--------|-------|----|---------| -----------| | Patients | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | | Records | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | | Appointments | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | | Bills | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | | Inventory | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | | Medications | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | | Vitals | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | | Lab Orders | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |

Troubleshooting
Common Issues
Database table errors: Run python seed.py to initialize the database.

Migration conflicts: Use flask db upgrade to apply migrations.

Port already in use: Kill the existing process or use a different port:

lsof -ti:5000 | xargs kill -9
Permission errors: Ensure proper role assignments in the database.

Quick Reset
# Reset SQLite database
rm -f hmis.db && python seed.py

# Reset PostgreSQL database
dropdb hmis_db && createdb hmis_db && python seed.py
Debug Mode
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
Testing
Unit Tests
python -m pytest tests/ -v
API Testing with curl
# Test login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Test protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:5000/api/patients
Contributing
Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
License
This project is licensed under the MIT License - see the LICENSE file for details.

Support
For support and questions, please open an issue on the project repository.

Changelog
Version 1.0.0
Initial release with core HMIS functionality
Multi-role authentication system
Patient management and medical records
Appointment scheduling and billing
Inventory and pharmacy management
Laboratory and radiology integration
Comprehensive audit logging
