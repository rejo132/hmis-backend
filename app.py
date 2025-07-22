from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, date
from flask_cors import CORS
import os

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Renamed from password_hash
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    email = db.Column(db.String(120), nullable=True)  # Added for /api/login
    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'))

    @property
    def role(self):
        return self.roles[0].name if self.roles else None

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

class LoginActivity(db.Model):
    __tablename__ = 'login_activity'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    contact = db.Column(db.String(50))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contact'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(50), nullable=False)

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    patient = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Scheduled')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient': self.patient,
            'date': self.date.isoformat(),
            'doctor_id': self.doctor_id,
            'reason': self.reason,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }

class Registration(db.Model):
    __tablename__ = 'registration'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    visit_type = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Inpatient(db.Model):
    __tablename__ = 'inpatient'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    admission_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    discharge_date = db.Column(db.DateTime)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    bed_id = db.Column(db.Integer, db.ForeignKey('bed.id'))

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'))
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    vital_signs = db.Column(db.JSON)
    symptoms = db.Column(db.Text)
    history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'diagnosis_id': self.diagnosis_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'vital_signs': self.vital_signs,
            'symptoms': self.symptoms,
            'history': self.history,
            'allergies': self.allergies,
            'created_at': self.created_at.isoformat()
        }

class NursingNote(db.Model):
    __tablename__ = 'nursing_note'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    nurse_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class DoctorNote(db.Model):
    __tablename__ = 'doctor_note'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Diagnosis(db.Model):
    __tablename__ = 'diagnosis'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

class Medication(db.Model):
    __tablename__ = 'medication'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

class PharmacyStock(db.Model):
    __tablename__ = 'pharmacy_stock'
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class PharmacyOrder(db.Model):
    __tablename__ = 'pharmacy_order'
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ordered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='Pending')

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    shift_type = db.Column(db.String(50))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Payroll(db.Model):
    __tablename__ = 'payroll'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    salary = db.Column(db.Numeric(10, 2), nullable=False)
    bonus = db.Column(db.Numeric(10, 2), default=0.00)
    deductions = db.Column(db.Numeric(10, 2), default=0.00)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default='Pending')

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class ErrorLog(db.Model):
    __tablename__ = 'error_log'
    id = db.Column(db.Integer, primary_key=True)
    error_message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class ReportsGenerated(db.Model):
    __tablename__ = 'reports_generated'
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(100), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Ward(db.Model):
    __tablename__ = 'ward'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

class Bed(db.Model):
    __tablename__ = 'bed'
    id = db.Column(db.Integer, primary_key=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    bed_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Available')

class BedAllocation(db.Model):
    __tablename__ = 'bed_allocation'
    id = db.Column(db.Integer, primary_key=True)
    bed_id = db.Column(db.Integer, db.ForeignKey('bed.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    allocation_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    discharge_date = db.Column(db.DateTime)

class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    maintenance_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'created_at': self.created_at.isoformat()
        }

class SuppliesInventory(db.Model):
    __tablename__ = 'supplies_inventory'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50))
    address = db.Column(db.Text)

class PatientLogin(db.Model):
    __tablename__ = 'patient_login'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class PatientFeedback(db.Model):
    __tablename__ = 'patient_feedback'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Download(db.Model):
    __tablename__ = 'download'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    document_name = db.Column(db.String(100), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class AppointmentRequest(db.Model):
    __tablename__ = 'appointment_request'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    requested_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Bill(db.Model):
    __tablename__ = 'bill'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    payment_status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'amount': float(self.amount),
            'description': self.description,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat()
        }

class SecurityLog(db.Model):
    __tablename__ = 'security_log'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class LabSample(db.Model):
    __tablename__ = 'lab_sample'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    sample_type = db.Column(db.String(50), nullable=False)
    collection_time = db.Column(db.DateTime, nullable=False)
    collected_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'sample_type': self.sample_type,
            'collection_time': self.collection_time.isoformat(),
            'collected_by': self.collected_by,
            'created_at': self.created_at.isoformat()
        }

class Vitals(db.Model):
    __tablename__ = 'vitals'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    blood_pressure = db.Column(db.String(20), nullable=False)
    temperature = db.Column(db.Numeric(4, 1), nullable=False)
    pulse = db.Column(db.Integer, nullable=False)
    respiration = db.Column(db.Integer, nullable=False)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'blood_pressure': self.blood_pressure,
            'temperature': float(self.temperature),
            'pulse': self.pulse,
            'respiration': self.respiration,
            'recorded_by': self.recorded_by,
            'recorded_at': self.recorded_at.isoformat()
        }

class Communication(db.Model):
    __tablename__ = 'communication_settings'
    id = db.Column(db.Integer, primary_key=True)
    sms = db.Column(db.Boolean, nullable=False, default=False)
    email = db.Column(db.Boolean, nullable=False, default=False)
    chat = db.Column(db.Boolean, nullable=False, default=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'sms': self.sms,
            'email': self.email,
            'chat': self.chat,
            'updated_at': self.updated_at.isoformat()
        }

class LabOrder(db.Model):
    __tablename__ = 'lab_order'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    results = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'test_type': self.test_type,
            'status': self.status,
            'results': self.results,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }

class RadiologyOrder(db.Model):
    __tablename__ = 'radiology_order'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    results = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'test_type': self.test_type,
            'status': self.status,
            'results': self.results,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }

# Helper function to check user role
def has_role(user, role_name):
    if isinstance(role_name, list):
        # Handle multiple roles by checking if user has any of them
        return Role.query.join(UserRole).filter(
            UserRole.user_id == user.id, 
            Role.name.in_(role_name)
        ).first() is not None
    else:
        # Handle single role
        return Role.query.join(UserRole).filter(
            UserRole.user_id == user.id, 
            Role.name == role_name
        ).first() is not None


# Routes
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to HMIS API'}), 200

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        user_count = User.query.count()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users': user_count,
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return jsonify({'message': 'Missing required fields: username, password, role'}), 422
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    try:
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            role_obj = Role(name=role)
            db.session.add(role_obj)
            db.session.commit()
        user_role = UserRole(user_id=user.id, role_id=role_obj.id)
        db.session.add(user_role)
        audit_log = AuditLog(action='User registered', user=username)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'User registered'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=None)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error registering user'}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing required fields: username, password'}), 422
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'email': user.email or ''
            }
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'logs': [{'id': log.id, 'action': log.action, 'user': log.user, 'timestamp': log.timestamp.isoformat()} for log in logs.items],
        'total': logs.total,
        'pages': logs.pages
    }), 200

@app.route('/api/security-logs', methods=['GET'])
@jwt_required()
def get_security_logs():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'IT'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'logs': [{'id': log.id, 'event': log.event, 'user': log.user, 'status': log.status, 'timestamp': log.timestamp.isoformat()} for log in logs.items],
        'total': logs.total,
        'pages': logs.pages
    }), 200

@app.route('/api/patients', methods=['POST'])
@jwt_required()
def add_patient():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('name') or not data.get('dob'):
        return jsonify({'message': 'Missing required fields: name, dob'}), 422
    try:
        dob = datetime.strptime(data.get('dob'), '%Y-%m-%d').date()
        patient = Patient(
            name=data.get('name'),
            dob=dob,
            contact=data.get('contact'),
            address=data.get('address')
        )
        db.session.add(patient)
        db.session.commit()
        medical_record = MedicalRecord(
            patient_id=patient.id,
            doctor_id=user.id,
            diagnosis='Initial assessment',
            history=data.get('medical_history'),
            allergies=data.get('allergies')
        )
        db.session.add(medical_record)
        audit_log = AuditLog(action='Patient added', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Patient added'}), 201
    except ValueError as ve:
        db.session.rollback()
        error_log = ErrorLog(error_message=f'Invalid date format: {str(ve)}', user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Invalid date format for dob'}), 422
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error adding patient'}), 500

@app.route('/api/patients', methods=['GET'])
@jwt_required()
def get_patients():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, ['Admin', 'Doctor', 'IT', 'Nurse', 'Receptionist']):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    patients = Patient.query.order_by(Patient.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'patients': [{
            'id': p.id,
            'name': p.name,
            'dob': p.dob.isoformat() if p.dob else None,
            'contact': p.contact,
            'address': p.address,
            'created_at': p.created_at.isoformat()
        } for p in patients.items],
        'total': patients.total,
        'pages': patients.pages
    }), 200

@app.route('/api/patients/<int:id>', methods=['GET'])
@jwt_required()
def get_patient(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin') and not has_role(user, 'Doctor'):
        return jsonify({'message': 'Unauthorized access'}), 403
    patient = db.session.get(Patient, id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    medical_record = MedicalRecord.query.filter_by(patient_id=id).first()
    return jsonify({
        'id': patient.id,
        'name': patient.name,
        'dob': patient.dob.isoformat(),
        'contact': patient.contact,
        'address': patient.address,
        'medical_history': medical_record.history if medical_record else None,
        'allergies': medical_record.allergies if medical_record else None
    }), 200

@app.route('/api/patients/<int:id>', methods=['PUT'])
@jwt_required()
def update_patient(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    patient = db.session.get(Patient, id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 422
    try:
        patient.name = data.get('name', patient.name)
        patient.contact = data.get('contact', patient.contact)
        patient.address = data.get('address', patient.address)
        db.session.commit()
        audit_log = AuditLog(action='Patient updated', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Patient updated'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error updating patient'}), 500

@app.route('/api/appointments', methods=['POST'])
@jwt_required()
def schedule_appointment():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('patient_id') or not data.get('doctor_id') or not data.get('appointment_time'):
        return jsonify({'message': 'Missing required fields: patient_id, doctor_id, appointment_time'}), 422
    try:
        patient = db.session.get(Patient, data.get('patient_id'))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        doctor = db.session.get(User, data.get('doctor_id'))
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404
        appointment_time = datetime.fromisoformat(data.get('appointment_time'))
        appointment = Appointment(
            patient=patient.id,
            doctor_id=doctor.id,
            date=appointment_time,
            reason=data.get('reason'),
            created_by=user.id
        )
        db.session.add(appointment)
        audit_log = AuditLog(action='Appointment scheduled', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Appointment scheduled'}), 201
    except ValueError as ve:
        db.session.rollback()
        error_log = ErrorLog(error_message=f'Invalid date format: {str(ve)}', user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Invalid date format for appointment_time'}), 422
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error scheduling appointment'}), 500

@app.route('/api/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin') and not has_role(user, 'Doctor'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = Appointment.query
    if has_role(user, 'Doctor'):
        query = query.filter_by(doctor_id=user.id)
    appointments = query.order_by(Appointment.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'appointments': [a.to_dict() for a in appointments.items],
        'total': appointments.total,
        'pages': appointments.pages
    }), 200

@app.route('/api/records', methods=['POST'])
@jwt_required()
def add_record():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Doctor'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('patient_id') or not data.get('diagnosis'):
        return jsonify({'message': 'Missing required fields: patient_id, diagnosis'}), 422
    try:
        patient = db.session.get(Patient, data.get('patient_id'))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        record = MedicalRecord(
            patient_id=patient.id,
            doctor_id=user.id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            vital_signs=data.get('vital_signs')
        )
        db.session.add(record)
        audit_log = AuditLog(action='Medical record added', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Record added'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error adding record'}), 500

@app.route('/api/records', methods=['GET'])
@jwt_required()
def get_records():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or (not has_role(user, 'Admin') and not has_role(user, 'Doctor') and not has_role(user, 'Nurse')):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = MedicalRecord.query
    if has_role(user, 'Doctor') or has_role(user, 'Nurse'):
        query = query.filter_by(doctor_id=user.id)
    records = query.order_by(MedicalRecord.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'records': [r.to_dict() for r in records.items],
        'total': records.total,
        'pages': records.pages,
        'page': page
    }), 200

@app.route('/api/bills', methods=['POST'])
@jwt_required()
def create_bill():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('patient_id') or not data.get('amount'):
        return jsonify({'message': 'Missing required fields: patient_id, amount'}), 422
    try:
        patient = db.session.get(Patient, data.get('patient_id'))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        bill = Bill(
            patient_id=patient.id,
            amount=data.get('amount'),
            description=data.get('description')
        )
        db.session.add(bill)
        audit_log = AuditLog(action='Bill created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Bill created'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating bill'}), 500

@app.route('/api/bills/<int:id>', methods=['PUT'])
@jwt_required()
def update_bill(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    bill = db.session.get(Bill, id)
    if not bill:
        return jsonify({'message': 'Bill not found'}), 404
    data = request.get_json()
    if not data or not data.get('payment_status'):
        return jsonify({'message': 'Missing required field: payment_status'}), 422
    try:
        bill.payment_status = data.get('payment_status')
        db.session.commit()
        audit_log = AuditLog(action='Bill updated', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Bill updated'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error updating bill'}), 500

@app.route('/api/bills', methods=['GET'])
@jwt_required()
def get_bills():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    bills = Bill.query.order_by(Bill.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'bills': [b.to_dict() for b in bills.items],
        'total': bills.total,
        'pages': bills.pages,
        'page': page
    }), 200

@app.route('/api/lab-orders', methods=['POST'])
@jwt_required()
def create_lab_order():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Doctor') and not has_role(user, 'Lab Tech'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('patient_id') or not data.get('test_type'):
        return jsonify({'message': 'Missing required fields: patient_id, test_type'}), 422
    try:
        patient = db.session.get(Patient, data.get('patient_id'))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        lab_order = LabOrder(
            patient_id=patient.id,
            test_type=data.get('test_type'),
            status='Pending',
            created_by=user.id
        )
        db.session.add(lab_order)
        audit_log = AuditLog(action='Lab order created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Lab order created'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating lab order'}), 500

@app.route('/api/radiology-orders', methods=['POST'])
@jwt_required()
def create_radiology_order():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Doctor'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('patient_id') or not data.get('test_type'):
        return jsonify({'message': 'Missing required fields: patient_id, test_type'}), 422
    try:
        patient = db.session.get(Patient, data.get('patient_id'))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        radiology_order = RadiologyOrder(
            patient_id=patient.id,
            test_type=data.get('test_type'),
            status='Pending',
            created_by=user.id
        )
        db.session.add(radiology_order)
        audit_log = AuditLog(action='Radiology order created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Radiology order created'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating radiology order'}), 500

@app.route('/api/employees', methods=['GET'])
@jwt_required()
def get_employees():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    employees = User.query.join(UserRole).join(Role).filter(Role.name.in_(['Doctor', 'Nurse', 'Admin', 'Lab Tech', 'IT'])).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'employees': [{
            'id': emp.id,
            'username': emp.username,
            'role': Role.query.join(UserRole).filter(UserRole.user_id == emp.id).first().name
        } for emp in employees.items],
        'total': employees.total,
        'pages': employees.pages
    }), 200

@app.route('/api/employees', methods=['POST'])
@jwt_required()
def create_employee():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('role'):
        return jsonify({'message': 'Missing required fields: username, password, role'}), 422
    try:
        if User.query.filter_by(username=data.get('username')).first():
            return jsonify({'message': 'Username already exists'}), 400
        employee = User(
            username=data.get('username'),
            password=generate_password_hash(data.get('password'))
        )
        db.session.add(employee)
        db.session.commit()
        role = Role.query.filter_by(name=data.get('role')).first()
        if not role:
            role = Role(name=data.get('role'))
            db.session.add(role)
            db.session.commit()
        user_role = UserRole(user_id=employee.id, role_id=role.id)
        db.session.add(user_role)
        audit_log = AuditLog(action='Employee created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Employee created'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating employee'}), 500

@app.route('/api/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    employee = db.session.get(User, id)
    if not employee:
        return jsonify({'message': 'Employee not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 422
    try:
        employee.username = data.get('username', employee.username)
        if data.get('password'):
            employee.password = generate_password_hash(data.get('password'))
        db.session.commit()
        if data.get('role'):
            role = Role.query.filter_by(name=data.get('role')).first()
            if not role:
                role = Role(name=data.get('role'))
                db.session.add(role)
                db.session.commit()
            user_role = UserRole.query.filter_by(user_id=id).first()
            if user_role:
                user_role.role_id = role.id
            else:
                user_role = UserRole(user_id=id, role_id=role.id)
                db.session.add(user_role)
        audit_log = AuditLog(action='Employee updated', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Employee updated'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error updating employee'}), 500

@app.route('/api/finance/expenses', methods=['GET'])
@jwt_required()
def get_finance_expenses():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    expenses = Payroll.query.filter(Payroll.deductions > 0).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'expenses': [{
            'id': exp.id,
            'user_id': exp.user_id,
            'amount': float(exp.deductions),
            'description': 'Payroll deduction'
        } for exp in expenses.items],
        'total': expenses.total,
        'pages': expenses.pages
    }), 200

@app.route('/api/finance/reimbursements', methods=['GET'])
@jwt_required()
def get_finance_reimbursements():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    reimbursements = Payroll.query.filter(Payroll.bonus > 0).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'reimbursements': [{
            'id': r.id,
            'user_id': r.user_id,
            'amount': float(r.bonus),
            'description': 'Payroll bonus'
        } for r in reimbursements.items],
        'total': reimbursements.total,
        'pages': reimbursements.pages
    }), 200

@app.route('/api/finance/payroll', methods=['GET'])
@jwt_required()
def get_finance_payroll():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    payroll = Payroll.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'payroll': [{
            'id': p.id,
            'user_id': p.user_id,
            'salary': float(p.salary),
            'bonus': float(p.bonus),
            'deductions': float(p.deductions),
            'period_start': p.period_start.isoformat(),
            'period_end': p.period_end.isoformat()
        } for p in payroll.items],
        'total': payroll.total,
        'pages': payroll.pages
    }), 200

@app.route('/api/finance/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('amount'):
        return jsonify({'message': 'Missing required fields: user_id, amount'}), 422
    try:
        payroll = Payroll(
            user_id=data.get('user_id'),
            salary=0.00,
            deductions=data.get('amount'),
            period_start=datetime.now(timezone.utc).date(),
            period_end=datetime.now(timezone.utc).date()
        )
        db.session.add(payroll)
        audit_log = AuditLog(action='Expense created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Expense created'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating expense'}), 500

@app.route('/api/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, ['Admin', 'Pharmacist', 'Nurse', 'Doctor']):
        return jsonify({'message': 'Unauthorized access'}), 403
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        inventory = SuppliesInventory.query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({
            'items': [{
                'id': item.id,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'last_updated': item.last_updated.isoformat()
            } for item in inventory.items],
            'total': inventory.total,
            'pages': inventory.pages
        }), 200
    except Exception as e:
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error fetching inventory'}), 500

@app.route('/api/inventory', methods=['POST'])
@jwt_required()
def create_inventory():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('item_name') or not data.get('quantity'):
        return jsonify({'message': 'Missing required fields: item_name, quantity'}), 422
    try:
        item = SuppliesInventory(
            item_name=data.get('item_name'),
            quantity=data.get('quantity')
        )
        db.session.add(item)
        audit_log = AuditLog(action='Inventory item created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Inventory item created'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating inventory item'}), 500

@app.route('/api/inventory/<int:id>', methods=['PUT'])
@jwt_required()
def update_inventory(id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    item = db.session.get(SuppliesInventory, id)
    if not item:
        return jsonify({'message': 'Inventory item not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 422
    try:
        item.item_name = data.get('item_name', item.item_name)
        item.quantity = data.get('quantity', item.quantity)
        item.last_updated = datetime.now(timezone.utc)
        db.session.commit()
        audit_log = AuditLog(action='Inventory item updated', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Inventory item updated'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error updating inventory item'}), 500

@app.route('/api/inventory/dispense', methods=['POST'])
@jwt_required()
def dispense_medication():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin') and not has_role(user, 'Doctor'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('item_id') or not data.get('quantity'):
        return jsonify({'message': 'Missing required fields: item_id, quantity'}), 422
    try:
        item = db.session.get(SuppliesInventory, data.get('item_id'))
        if not item:
            return jsonify({'message': 'Inventory item not found'}), 404
        if item.quantity < data.get('quantity'):
            return jsonify({'message': 'Insufficient quantity'}), 400
        item.quantity -= data.get('quantity')
        item.last_updated = datetime.now(timezone.utc)
        db.session.commit()
        audit_log = AuditLog(action='Medication dispensed', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Medication dispensed'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error dispensing medication'}), 500

@app.route('/api/medications', methods=['POST'])
@jwt_required()
def create_medication():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, ['Admin', 'Doctor', 'Nurse', 'Pharmacist']):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    
    # Handle different field name variations
    name = data.get('name') or data.get('medication_name') or data.get('medicationName')
    description = data.get('description') or data.get('notes') or ''
    dosage = data.get('dosage') or ''
    frequency = data.get('frequency') or ''
    
    if not data or not name:
        return jsonify({'message': 'Missing required field: name'}), 422
    
    try:
        medication = Medication(
            name=name,
            description=description
        )
        db.session.add(medication)
        audit_log = AuditLog(action=f'Medication created: {name}', user=user.username)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Medication created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating medication'}), 500

@app.route('/api/lab-samples', methods=['POST'])
@jwt_required()
def create_sample():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Lab Tech'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('patient_id') or not data.get('sample_type') or not data.get('collection_time'):
        return jsonify({'message': 'Missing required fields: patient_id, sample_type, collection_time'}), 422
    try:
        patient = db.session.get(Patient, data.get('patient_id'))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        collection_time = datetime.fromisoformat(data.get('collection_time'))
        sample = LabSample(
            patient_id=patient.id,
            sample_type=data.get('sample_type'),
            collection_time=collection_time,
            collected_by=user.id
        )
        db.session.add(sample)
        audit_log = AuditLog(action='Lab sample created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Lab sample created'}), 201
    except ValueError as ve:
        db.session.rollback()
        error_log = ErrorLog(error_message=f'Invalid date format: {str(ve)}', user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Invalid date format for collection_time'}), 422
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating lab sample'}), 500

@app.route('/api/shifts', methods=['GET'])
@jwt_required()
def get_shifts():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    shifts = Schedule.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'shifts': [{
            'id': shift.id,
            'user_id': shift.user_id,
            'start_time': shift.start_time.isoformat(),
            'end_time': shift.end_time.isoformat(),
            'shift_type': shift.shift_type
        } for shift in shifts.items],
        'total': shifts.total,
        'pages': shifts.pages
    }), 200

@app.route('/api/shifts', methods=['POST'])
@jwt_required()
def create_shift():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('start_time') or not data.get('end_time') or not data.get('shift_type'):
        return jsonify({'message': 'Missing required fields: user_id, start_time, end_time, shift_type'}), 422
    try:
        employee = db.session.get(User, data.get('user_id'))
        if not employee:
            return jsonify({'message': 'Employee not found'}), 404
        start_time = datetime.fromisoformat(data.get('start_time'))
        end_time = datetime.fromisoformat(data.get('end_time'))
        shift = Schedule(
            user_id=employee.id,
            start_time=start_time,
            end_time=end_time,
            shift_type=data.get('shift_type')
        )
        db.session.add(shift)
        audit_log = AuditLog(action='Shift created', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Shift created'}), 201
    except ValueError as ve:
        db.session.rollback()
        error_log = ErrorLog(error_message=f'Invalid date format: {str(ve)}', user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Invalid date format for start_time or end_time'}), 422
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error creating shift'}), 500

@app.route('/api/settings', methods=['GET'])
@jwt_required()
def get_settings():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    settings = Communication.query.first() or Communication()
    return jsonify(settings.to_dict()), 200

@app.route('/api/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 422
    try:
        settings = Communication.query.first() or Communication()
        settings.sms = data.get('sms', settings.sms)
        settings.email = data.get('email', settings.email)
        settings.chat = data.get('chat', settings.chat)
        settings.updated_at = datetime.now(timezone.utc)
        db.session.add(settings)
        audit_log = AuditLog(action='Settings updated', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Settings updated'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error updating settings'}), 500

@app.route('/api/users/roles', methods=['GET'])
@jwt_required()
def get_user_roles():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    roles = UserRole.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'roles': [{
            'id': role.id,
            'user_id': role.user_id,
            'role': Role.query.get(role.role_id).name
        } for role in roles.items],
        'total': roles.total,
        'pages': roles.pages
    }), 200

@app.route('/api/users/roles', methods=['PUT'])
@jwt_required()
def update_user_role():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('role'):
        return jsonify({'message': 'Missing required fields: user_id, role'}), 422
    try:
        user_role = UserRole.query.filter_by(user_id=data.get('user_id')).first()
        if not user_role:
            return jsonify({'message': 'User role not found'}), 404
        role = Role.query.filter_by(name=data.get('role')).first()
        if not role:
            role = Role(name=data.get('role'))
            db.session.add(role)
            db.session.commit()
        user_role.role_id = role.id
        db.session.commit()
        audit_log = AuditLog(action='User role updated', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'User role updated'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error updating user role'}), 500

@app.route('/api/vitals', methods=['POST'])
@jwt_required()
def create_vitals():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, ['Nurse', 'Doctor', 'Admin']):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    
    # Handle different field name variations
    patient_id = data.get('patient_id') or data.get('patientId')
    blood_pressure = data.get('blood_pressure') or data.get('bloodPressure') or data.get('bp')
    temperature = data.get('temperature') or data.get('temp')
    pulse = data.get('pulse') or data.get('heart_rate') or data.get('heartRate')
    respiration = data.get('respiration') or data.get('respiratory_rate') or data.get('respiratoryRate')
    
    if not data or not patient_id:
        return jsonify({'message': 'Missing required field: patient_id'}), 422
    
    try:
        patient = db.session.get(Patient, int(patient_id))
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
            
        vitals = Vitals(
            patient_id=patient.id,
            blood_pressure=blood_pressure or '120/80',
            temperature=float(temperature) if temperature else 98.6,
            pulse=int(pulse) if pulse else 70,
            respiration=int(respiration) if respiration else 16,
            recorded_by=user.id
        )
        db.session.add(vitals)
        audit_log = AuditLog(action=f'Vitals recorded for Patient #{patient_id}', user=user.username)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Vitals recorded successfully'}), 201
    except ValueError:
        return jsonify({'message': 'Invalid data format for vital signs'}), 422
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error recording vitals'}), 500

@app.route('/api/assets', methods=['GET'])
@jwt_required()
def get_assets():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    page = request.args.get('page', 1, type=int)
    per_page = 10
    assets = Equipment.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'assets': [asset.to_dict() for asset in assets.items],
        'total': assets.total,
        'pages': assets.pages
    }), 200

@app.route('/api/assets/maintenance', methods=['POST'])
@jwt_required()
def schedule_maintenance():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    
    # Handle both object and direct value formats
    if isinstance(data, dict):
        asset_id = data.get('assetId')
        maintenance_date_str = data.get('maintenance_date')
    else:
        # If data is not a dict, treat it as assetId
        asset_id = data
        maintenance_date_str = None
    
    if not asset_id:
        return jsonify({'message': 'Missing required field: assetId'}), 422
    try:
        asset = db.session.get(Equipment, asset_id)
        if not asset:
            return jsonify({'message': 'Asset not found'}), 404
        if maintenance_date_str:
            maintenance_date = datetime.fromisoformat(maintenance_date_str)
        else:
            maintenance_date = datetime.now(timezone.utc)
        asset.maintenance_date = maintenance_date
        asset.status = 'Maintenance'
        db.session.commit()
        audit_log = AuditLog(action='Asset maintenance scheduled', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify(asset.to_dict()), 200
    except ValueError as ve:
        db.session.rollback()
        error_log = ErrorLog(error_message=f'Invalid date format: {str(ve)}', user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Invalid date format for maintenance_date'}), 422
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error scheduling maintenance'}), 500

@app.route('/api/beds', methods=['GET'])
@jwt_required()
def get_beds():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, ['Admin', 'Nurse']):
        return jsonify({'message': 'Unauthorized access'}), 403
    try:
        beds = Bed.query.all()
        beds_data = []
        for bed in beds:
            # Get current allocation if any
            allocation = BedAllocation.query.filter_by(bed_id=bed.id, discharge_date=None).first()
            beds_data.append({
                'id': bed.id,
                'ward': bed.ward_id,
                'bed_number': bed.bed_number,
                'status': bed.status,
                'patient_id': allocation.patient_id if allocation else None
            })
        return jsonify({'beds': beds_data}), 200
    except Exception as e:
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error fetching beds'}), 500

@app.route('/api/beds/reserve', methods=['POST'])
@jwt_required()
def reserve_bed():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    
    # Handle both object and direct value formats
    if isinstance(data, dict):
        bed_id = data.get('bedId')
        patient_id = data.get('patient_id')
    else:
        # If data is not a dict, treat it as bedId and use default patient_id
        bed_id = data
        patient_id = 1  # Default patient ID for reservation
    
    if not bed_id:
        return jsonify({'message': 'Missing required field: bedId'}), 422
    try:
        bed = db.session.get(Bed, bed_id)
        if not bed:
            return jsonify({'message': 'Bed not found'}), 404
        patient = db.session.get(Patient, patient_id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404
        if bed.status != 'Available':
            return jsonify({'message': 'Bed not available'}), 400
        bed.status = 'Reserved'
        bed_allocation = BedAllocation(
            bed_id=bed.id,
            patient_id=patient.id
        )
        db.session.add(bed_allocation)
        audit_log = AuditLog(action='Bed reserved', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Bed reserved'}), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error reserving bed'}), 500

@app.route('/api/bills/refund', methods=['POST'])
@jwt_required()
def process_refund():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('billId'):
        return jsonify({'message': 'Missing required field: billId'}), 422
    try:
        bill = db.session.get(Bill, data.get('billId'))
        if not bill:
            return jsonify({'message': 'Bill not found'}), 404
        bill.payment_status = 'Refunded'
        db.session.commit()
        audit_log = AuditLog(action='Bill refunded', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Refund processed'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error processing refund'}), 500

@app.route('/api/bills/claim', methods=['POST'])
@jwt_required()
def process_claim():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('billId'):
        return jsonify({'message': 'Missing required field: billId'}), 422
    try:
        bill = db.session.get(Bill, data.get('billId'))
        if not bill:
            return jsonify({'message': 'Bill not found'}), 404
        bill.payment_status = 'Claimed'
        db.session.commit()
        audit_log = AuditLog(action='Bill claim submitted', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Claim submitted'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error submitting claim'}), 500

@app.route('/api/communication-settings', methods=['GET'])
@jwt_required()
def get_communication_settings():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    settings = Communication.query.first() or Communication(sms=False, email=False, chat=False)
    return jsonify(settings.to_dict()), 200

@app.route('/api/communication-settings', methods=['PUT'])
@jwt_required()
def toggle_communication_setting():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('setting'):
        return jsonify({'message': 'Missing required field: setting'}), 422
    try:
        settings = Communication.query.first() or Communication()
        setting = data.get('setting')
        if setting not in ['sms', 'email', 'chat']:
            return jsonify({'message': 'Invalid setting'}), 400
        setattr(settings, setting, not getattr(settings, setting))
        settings.updated_at = datetime.now(timezone.utc)
        db.session.add(settings)
        audit_log = AuditLog(action=f'Communication setting {setting} toggled', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify(settings.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error toggling communication setting'}), 500

@app.route('/api/communications', methods=['POST'])
@jwt_required()
def add_communication():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    if not user or not has_role(user, 'Admin'):
        return jsonify({'message': 'Unauthorized access'}), 403
    data = request.get_json()
    if not data or not data.get('user_id') or not data.get('message'):
        return jsonify({'message': 'Missing required fields: user_id, message'}), 422
    try:
        notification = Notification(
            user_id=data.get('user_id'),
            message=data.get('message'),
            status='Pending'
        )
        db.session.add(notification)
        audit_log = AuditLog(action='Communication sent', user=current_user)
        db.session.add(audit_log)
        db.session.commit()
        return jsonify({'message': 'Communication sent'}), 201
    except Exception as e:
        db.session.rollback()
        error_log = ErrorLog(error_message=str(e), user_id=user.id)
        db.session.add(error_log)
        db.session.commit()
        return jsonify({'message': 'Error sending communication'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)