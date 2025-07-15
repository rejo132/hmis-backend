import pytest
from app import app, db, User, Patient, Appointment, MedicalRecord, Bill
import os
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('hmis_db', 'hmis_test')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass',
        'role': 'Doctor'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered'

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
    return response.json['token']

def test_add_patient(client):
    token = test_login(client)
    response = client.post('/api/patients', json={
        'name': 'John Doe',
        'dob': '1990-01-01',
        'contact': '1234567890',
        'address': '123 Main St',
        'medical_history': 'None',
        'allergies': 'Penicillin'
    }, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 403  # Fails due to non-Admin role
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

def test_get_patients(client):
    token = test_login(client)
    response = client.get('/api/patients?page=1', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'patients' in response.json
    assert 'total' in response.json
    assert 'pages' in response.json

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

def test_get_appointments(client):
    token = test_login(client)
    response = client.get('/api/appointments?page=1', headers={'Authorization': f'Bearer {token}'})
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