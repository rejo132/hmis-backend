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

## Installation

### Prerequisites

- Python 3.13 or higher
- SQLite (default) or PostgreSQL

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hmis-backend
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python init_db.py  # Creates tables and loads sample data
   ```

6. **Run the application**
   ```bash
   python run.py
   # Or for development:
   FLASK_ENV=development python run.py
   ```

## API Documentation

### Authentication

The API uses JWT tokens for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### Authentication
- `POST /api/login` - User login
- `POST /api/register` - User registration

#### Patient Management
- `GET /api/patients` - List all patients
- `POST /api/patients` - Create new patient
- `GET /api/patients/{id}` - Get patient details
- `PUT /api/patients/{id}` - Update patient

#### Medical Records
- `GET /api/records` - List medical records
- `POST /api/records` - Create new medical record

#### Appointments
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Schedule appointment

#### Billing
- `GET /api/bills` - List bills
- `POST /api/bills` - Create bill
- `PUT /api/bills/{id}` - Update bill status

#### Inventory
- `GET /api/inventory` - List inventory items
- `POST /api/inventory` - Add inventory item
- `PUT /api/inventory/{id}` - Update inventory
- `POST /api/inventory/dispense` - Dispense medication

#### Laboratory
- `POST /api/lab-orders` - Create lab order
- `POST /api/lab-samples` - Record lab sample

#### Administration
- `GET /api/employees` - List employees
- `POST /api/employees` - Create employee
- `GET /api/audit-logs` - View audit logs
- `GET /api/settings` - Get system settings

### Sample Requests

#### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

#### Get Patients
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/patients
```

## Default Users

After running `seed.py`, the following users are available:

| Username | Password | Role |
|----------|----------|------|
| admin | password123 | Admin |
| doctor1 | password123 | Doctor |
| nurse1 | password123 | Nurse |
| it1 | password123 | IT |
| labtech1 | password123 | Lab Tech |

## Configuration

Environment variables (set in `.env`):

- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection string
- `FLASK_ENV` - Environment (development/production)

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Database Schema

The application includes comprehensive database models for:

- Users and Roles
- Patients and Emergency Contacts
- Medical Records and Diagnoses
- Appointments and Schedules
- Billing and Payments
- Inventory and Equipment
- Laboratory and Radiology Orders
- Audit Logs and Security

## Security Features

- JWT-based authentication
- Role-based access control
- Password hashing with scrypt
- Comprehensive audit logging
- Error logging and monitoring
- CORS support for frontend integration

## Development

### Running Tests

```bash
pytest tests/
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### API Testing

The application is configured with CORS to allow frontend connections from `http://localhost:3000`.

## Troubleshooting

### Common Issues

**Database table errors:** Run `python init_db.py` to initialize the database.

**Migration conflicts:** Use `python init_db.py` instead of Flask migrations.

**Port already in use:** Kill the existing process or use a different port.

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Quick Reset
```bash
python reset_db.py  # Reset database with confirmation
# or
rm -f hmis.db && python init_db.py  # Force reset
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the project repository.
