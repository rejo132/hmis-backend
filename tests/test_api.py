import pytest
import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db, User, Patient, Appointment, MedicalRecord, Bill, AuditLog, SecurityLog, Role, UserRole
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('hmis_db', 'hmis_test')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hmis_test.db'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass',
        'role': 'Doctor'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered'
    with app.app_context():
        user = db.session.get(User, User.query.filter_by(username='testuser').first().id)
        assert user is not None
        role = db.session.get(Role, Role.query.filter_by(name='Doctor').first().id)
        assert role is not None
        user_role = db.session.get(UserRole, UserRole.query.filter_by(user_id=user.id, role_id=role.id).first().id)
        assert user_role is not None
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='User registered', user='testuser').first().id)
        assert audit_log is not None

def test_login(client):
    client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass',
        'role': 'Doctor'
    })
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['role'] == 'Doctor'
    with app.app_context():
        security_log = db.session.get(SecurityLog, SecurityLog.query.filter_by(event='Login attempt', user='testuser', status='Success').first().id)
        assert security_log is not None

def test_audit_logs(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    with app.app_context():
        db.session.add(AuditLog(action='Test action', user='adminuser', timestamp=datetime.now(timezone.utc)))
        db.session.commit()
    response = client.get('/api/audit-logs?page=1', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert 'logs' in response.json
    assert any(log['action'] == 'Test action' for log in response.json['logs'])

def test_security_logs(client):
    client.post('/api/register', json={
        'username': 'ituser',
        'password': 'itpass',
        'role': 'IT'
    })
    it_response = client.post('/api/login', json={
        'username': 'ituser',
        'password': 'itpass'
    })
    it_token = it_response.json['token']
    with app.app_context():
        db.session.add(SecurityLog(event='Test event', user='ituser', status='Success', timestamp=datetime.now(timezone.utc)))
        db.session.commit()
    response = client.get('/api/security-logs?page=1', headers={'Authorization': f'Bearer {it_token}'})
    assert response.status_code == 200
    assert 'logs' in response.json
    assert any(log['event'] == 'Test event' for log in response.json['logs'])

def test_add_patient(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    response = client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['message'] == 'Patient added'
    with app.app_context():
        patient = db.session.get(Patient, Patient.query.filter_by(name='John Doe').first().id)
        assert patient is not None
        medical_record = MedicalRecord.query.filter_by(patient_id=patient.id).first()
        assert medical_record.allergies == 'Penicillin'
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='Patient added', user='adminuser').first().id)
        assert audit_log is not None

def test_add_patient_unauthorized(client):
    client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass',
        'role': 'Doctor'
    })
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = response.json['token']
    response = client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403
    assert response.json['message'] == 'Unauthorized access'

def test_get_patients(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    response = client.get('/api/patients?page=1', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert 'patients' in response.json
    assert response.json['total'] >= 1
    assert response.json['pages'] >= 1
    assert any(patient['name'] == 'John Doe' for patient in response.json['patients'])

def test_get_patient(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    response = client.get('/api/patients/1', headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['name'] == 'John Doe'
    assert response.json['allergies'] == 'Penicillin'

def test_update_patient(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    response = client.put('/api/patients/1', json={
        'name': 'Jane Doe',
        'contact': '0987654321'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Patient updated'
    with app.app_context():
        patient = db.session.get(Patient, 1)
        assert patient.name == 'Jane Doe'
        assert patient.contact == '0987654321'
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='Patient updated', user='adminuser').first().id)
        assert audit_log is not None

def test_schedule_appointment(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    client.post('/api/register', json={
        'username': 'doctor',
        'password': 'docpass',
        'role': 'Doctor'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    response = client.post('/api/appointments', json={
        'patient_id': 1,
        'doctor_id': 2,
        'appointment_time': '2025-07-20T10:00:00'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['message'] == 'Appointment scheduled'
    with app.app_context():
        appointment = db.session.get(Appointment, 1)
        assert appointment.patient_id == 1
        assert appointment.doctor_id == 2
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='Appointment scheduled', user='adminuser').first().id)
        assert audit_log is not None

def test_get_appointments(client):
    client.post('/api/register', json={
        'username': 'doctor',
        'password': 'docpass',
        'role': 'Doctor'
    })
    doctor_response = client.post('/api/login', json={
        'username': 'doctor',
        'password': 'docpass'
    })
    doctor_token = doctor_response.json['token']
    response = client.get('/api/appointments?page=1', headers={'Authorization': f'Bearer {doctor_token}'})
    assert response.status_code == 200
    assert 'appointments' in response.json
    assert 'total' in response.json
    assert 'pages' in response.json

def test_add_record(client):
    client.post('/api/register', json={
        'username': 'doctor',
        'password': 'docpass',
        'role': 'Doctor'
    })
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    doctor_response = client.post('/api/login', json={
        'username': 'doctor',
        'password': 'docpass'
    })
    doctor_token = doctor_response.json['token']
    response = client.post('/api/records', json={
        'patient_id': 1,
        'diagnosis': 'Flu',
        'prescription': 'Rest, fluids',
        'vital_signs': {'heart_rate': 80, 'bp': '120/80'}
    }, headers={'Authorization': f'Bearer {doctor_token}'})
    assert response.status_code == 201
    assert response.json['message'] == 'Record added'
    with app.app_context():
        record = MedicalRecord.query.filter_by(patient_id=1).order_by(MedicalRecord.created_at.desc()).first()
        assert record.diagnosis == 'Flu'
        assert record.vital_signs == {'heart_rate': 80, 'bp': '120/80'}
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='Medical record added', user='doctor').first().id)
        assert audit_log is not None

def test_create_bill(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    response = client.post('/api/bills', json={
        'patient_id': 1,
        'amount': 100.00,
        'description': 'Consultation fee'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 201
    assert response.json['message'] == 'Bill created'
    with app.app_context():
        bill = db.session.get(Bill, 1)
        assert bill.amount == 100.00
        assert bill.description == 'Consultation fee'
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='Bill created', user='adminuser').first().id)
        assert audit_log is not None

def test_update_bill(client):
    client.post('/api/register', json={
        'username': 'adminuser',
        'password': 'adminpass',
        'role': 'Admin'
    })
    admin_response = client.post('/api/login', json={
        'username': 'adminuser',
        'password': 'adminpass'
    })
    admin_token = admin_response.json['token']
    client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    client.post('/api/bills', json={
        'patient_id': 1,
        'amount': 100.00,
        'description': 'Consultation fee'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    response = client.put('/api/bills/1', json={
        'payment_status': 'Paid'
    }, headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Bill updated'
    with app.app_context():
        bill = db.session.get(Bill, 1)
        assert bill.payment_status == 'Paid'
        audit_log = db.session.get(AuditLog, AuditLog.query.filter_by(action='Bill updated', user='adminuser').first().id)
        assert audit_log is not None