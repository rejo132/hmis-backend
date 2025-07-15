from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    contact = db.Column(db.String(50))
    address = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    vital_signs = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    payment_status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if not username or not password or not role:
        return jsonify({'error': 'Missing fields'}), 400
    if role not in ['Doctor', 'Nurse', 'Admin']:
        return jsonify({'error': 'Invalid role'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username exists'}), 400
    user = User(username=username, password_hash=generate_password_hash(password), role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        token = create_access_token(identity={'id': user.id, 'role': user.role})
        return jsonify({'token': token, 'role': user.role}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/patients', methods=['GET'])
@jwt_required()
def get_patients():
    identity = get_jwt_identity()
    if identity['role'] not in ['Doctor', 'Nurse', 'Admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    patients = Patient.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'patients': [{'id': p.id, 'name': p.name, 'dob': p.dob.isoformat(), 'contact': p.contact} for p in patients.items],
        'total': patients.total,
        'pages': patients.pages
    })

@app.route('/api/patients', methods=['POST'])
@jwt_required()
def add_patient():
    identity = get_jwt_identity()
    if identity['role'] != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    patient = Patient(
        name=data.get('name'),
        dob=datetime.strptime(data.get('dob'), '%Y-%m-%d'),
        contact=data.get('contact'),
        address=data.get('address'),
        medical_history=data.get('medical_history'),
        allergies=data.get('allergies')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient added'}), 201

@app.route('/api/patients/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    identity = get_jwt_identity()
    if identity['role'] not in ['Doctor', 'Nurse', 'Admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    patient = Patient.query.get_or_404(id)
    return jsonify({
        'id': patient.id,
        'name': patient.name,
        'dob': patient.dob.isoformat(),
        'contact': patient.contact,
        'address': patient.address,
        'medical_history': patient.medical_history,
        'allergies': patient.allergies
    })

@app.route('/api/patients/<int:id>', methods=['PUT'])
@jwt_required()
def update_patient(id):
    identity = get_jwt_identity()
    if identity['role'] != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    patient = Patient.query.get_or_404(id)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.dob = datetime.strptime(data.get('dob'), '%Y-%m-%d') if data.get('dob') else patient.dob
    patient.contact = data.get('contact', patient.contact)
    patient.address = data.get('address', patient.address)
    patient.medical_history = data.get('medical_history', patient.medical_history)
    patient.allergies = data.get('allergies', patient.allergies)
    db.session.commit()
    return jsonify({'message': 'Patient updated'})

@app.route('/api/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    identity = get_jwt_identity()
    if identity['role'] not in ['Doctor', 'Nurse', 'Admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    appointments = Appointment.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'appointments': [{'id': a.id, 'patient_id': a.patient_id, 'doctor_id': a.doctor_id, 'time': a.appointment_time.isoformat(), 'status': a.status} for a in appointments.items],
        'total': appointments.total,
        'pages': appointments.pages
    })

@app.route('/api/appointments', methods=['POST'])
@jwt_required()
def schedule_appointment():
    identity = get_jwt_identity()
    if identity['role'] != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    appointment = Appointment(
        patient_id=data.get('patient_id'),
        doctor_id=data.get('doctor_id'),
        appointment_time=datetime.strptime(data.get('appointment_time'), '%Y-%m-%dT%H:%M:%S')
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment scheduled'}), 201

@app.route('/api/records', methods=['POST'])
@jwt_required()
def add_record():
    identity = get_jwt_identity()
    if identity['role'] != 'Doctor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    record = MedicalRecord(
        patient_id=data.get('patient_id'),
        doctor_id=identity['id'],
        diagnosis=data.get('diagnosis'),
        prescription=data.get('prescription'),
        vital_signs=data.get('vital_signs')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': 'Record added'}), 201

@app.route('/api/bills', methods=['POST'])
@jwt_required()
def create_bill():
    identity = get_jwt_identity()
    if identity['role'] != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    bill = Bill(
        patient_id=data.get('patient_id'),
        amount=data.get('amount'),
        description=data.get('description')
    )
    db.session.add(bill)
    db.session.commit()
    return jsonify({'message': 'Bill created'}), 201

@app.route('/api/bills/<int:id>', methods=['PUT'])
@jwt_required()
def update_bill(id):
    identity = get_jwt_identity()
    if identity['role'] != 'Admin':
        return jsonify({'error': 'Unauthorized'}), 403
    bill = Bill.query.get_or_404(id)
    data = request.get_json()
    bill.payment_status = data.get('payment_status', bill.payment_status)
    db.session.commit()
    return jsonify({'message': 'Bill updated'})

if __name__ == '__main__':
    app.run(debug=True)