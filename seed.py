from flask import current_app
from app import app, db, User, Role, UserRole, LoginActivity, Patient, EmergencyContact, Appointment, Registration, Inpatient, MedicalRecord, NursingNote, DoctorNote, Diagnosis, Medication, PharmacyStock, PharmacyOrder, Schedule, Attendance, Payroll, Notification, AuditLog, ErrorLog, ReportsGenerated, Ward, Bed, BedAllocation, Equipment, SuppliesInventory, Vendor, PatientLogin, PatientFeedback, Download, AppointmentRequest, Bill, SecurityLog, LabSample, Vitals, Communication, LabOrder, RadiologyOrder
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

with app.app_context():
    db.drop_all()
    db.create_all()

    # Seed Roles
    roles = [
        {'name': 'Admin'},
        {'name': 'Doctor'},
        {'name': 'Nurse'},
        {'name': 'IT'},
        {'name': 'Lab Tech'},
    ]
    for role in roles:
        db.session.add(Role(**role))

    # Seed Users
    users = [
        {'username': 'admin', 'password': generate_password_hash('password123'), 'created_at': datetime.now(timezone.utc)},
        {'username': 'doctor1', 'password': generate_password_hash('password123'), 'created_at': datetime.now(timezone.utc)},
        {'username': 'nurse1', 'password': generate_password_hash('password123'), 'created_at': datetime.now(timezone.utc)},
        {'username': 'it1', 'password': generate_password_hash('password123'), 'created_at': datetime.now(timezone.utc)},
        {'username': 'labtech1', 'password': generate_password_hash('password123'), 'created_at': datetime.now(timezone.utc)},
    ]
    for user in users:
        db.session.add(User(**user))
    db.session.commit()

    # Seed UserRoles
    user_roles = [
        {'user_id': 1, 'role_id': 1},  # admin -> Admin
        {'user_id': 2, 'role_id': 2},  # doctor1 -> Doctor
        {'user_id': 3, 'role_id': 3},  # nurse1 -> Nurse
        {'user_id': 4, 'role_id': 4},  # it1 -> IT
        {'user_id': 5, 'role_id': 5},  # labtech1 -> Lab Tech
    ]
    for user_role in user_roles:
        db.session.add(UserRole(**user_role))

    # Seed LoginActivity
    login_activities = [
        {'user_id': 1, 'event': 'login', 'timestamp': datetime.now(timezone.utc)},
        {'user_id': 1, 'event': 'logout', 'timestamp': datetime.now(timezone.utc)},
    ]
    for activity in login_activities:
        db.session.add(LoginActivity(**activity))

    # Seed Patients
    patients = [
        {'name': 'John Doe', 'dob': datetime.strptime('1990-01-01', '%Y-%m-%d').date(), 'contact': '1234567890', 'address': '123 Main St', 'created_at': datetime.now(timezone.utc)},
        {'name': 'Jane Smith', 'dob': datetime.strptime('1985-05-15', '%Y-%m-%d').date(), 'contact': '0987654321', 'address': '456 Oak Ave', 'created_at': datetime.now(timezone.utc)},
    ]
    for patient in patients:
        db.session.add(Patient(**patient))
    db.session.commit()

    # Seed EmergencyContacts
    emergency_contacts = [
        {'patient_id': 1, 'name': 'Mary Doe', 'relationship': 'Spouse', 'contact': '1234567891'},
        {'patient_id': 2, 'name': 'John Smith', 'relationship': 'Brother', 'contact': '0987654322'},
    ]
    for contact in emergency_contacts:
        db.session.add(EmergencyContact(**contact))

    # Seed Appointments
    appointments = [
        {'patient': 1, 'doctor_id': 2, 'date': datetime.strptime('2025-07-20T10:00:00', '%Y-%m-%dT%H:%M:%S'), 'reason': 'Routine checkup', 'status': 'Scheduled', 'created_by': 1, 'created_at': datetime.now(timezone.utc)},
        {'patient': 2, 'doctor_id': 2, 'date': datetime.strptime('2025-07-21T14:00:00', '%Y-%m-%dT%H:%M:%S'), 'reason': 'Follow-up', 'status': 'Scheduled', 'created_by': 1, 'created_at': datetime.now(timezone.utc)},
    ]
    for appointment in appointments:
        db.session.add(Appointment(**appointment))

    # Seed Registrations
    registrations = [
        {'patient_id': 1, 'visit_type': 'New', 'registration_date': datetime.now(timezone.utc)},
        {'patient_id': 2, 'visit_type': 'Returning', 'registration_date': datetime.now(timezone.utc)},
    ]
    for registration in registrations:
        db.session.add(Registration(**registration))

    # Seed Wards
    wards = [
        {'name': 'General Ward', 'description': 'General patient care'},
        {'name': 'ICU', 'description': 'Intensive care unit'},
    ]
    for ward in wards:
        db.session.add(Ward(**ward))
    db.session.commit()

    # Seed Beds
    beds = [
        {'ward_id': 1, 'bed_number': 'G101', 'status': 'Available'},
        {'ward_id': 1, 'bed_number': 'G102', 'status': 'Occupied'},
    ]
    for bed in beds:
        db.session.add(Bed(**bed))
    db.session.commit()

    # Seed Inpatients
    inpatients = [
        {'patient_id': 1, 'admission_date': datetime.now(timezone.utc), 'ward_id': 1, 'bed_id': 2},
    ]
    for inpatient in inpatients:
        db.session.add(Inpatient(**inpatient))

    # Seed Diagnoses
    diagnoses = [
        {'code': 'J45', 'description': 'Asthma'},
        {'code': 'J11', 'description': 'Influenza'},
    ]
    for diagnosis in diagnoses:
        db.session.add(Diagnosis(**diagnosis))
    db.session.commit()

    # Seed MedicalRecords
    medical_records = [
        {'patient_id': 1, 'doctor_id': 2, 'diagnosis_id': 2, 'diagnosis': 'Flu', 'prescription': 'Rest, fluids', 'vital_signs': {'heart_rate': 80, 'bp': '120/80'}, 'symptoms': 'Fever, cough', 'history': 'None', 'allergies': 'Penicillin', 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'doctor_id': 2, 'diagnosis_id': 1, 'diagnosis': 'Asthma checkup', 'prescription': 'Inhaler', 'vital_signs': {'heart_rate': 75, 'bp': '118/78'}, 'symptoms': 'Wheezing', 'history': 'Chronic asthma', 'allergies': 'None', 'created_at': datetime.now(timezone.utc)},
    ]
    for record in medical_records:
        db.session.add(MedicalRecord(**record))

    # Seed NursingNotes
    nursing_notes = [
        {'patient_id': 1, 'nurse_id': 3, 'note': 'Patient stable, resting', 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'nurse_id': 3, 'note': 'Administered inhaler', 'created_at': datetime.now(timezone.utc)},
    ]
    for note in nursing_notes:
        db.session.add(NursingNote(**note))

    # Seed DoctorNotes
    doctor_notes = [
        {'patient_id': 1, 'doctor_id': 2, 'note': 'Prescribed rest and fluids', 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'doctor_id': 2, 'note': 'Continue inhaler, follow-up in 1 month', 'created_at': datetime.now(timezone.utc)},
    ]
    for note in doctor_notes:
        db.session.add(DoctorNote(**note))

    # Seed Medications
    medications = [
        {'name': 'Paracetamol', 'description': 'Pain reliever'},
        {'name': 'Albuterol', 'description': 'Asthma inhaler'},
    ]
    for medication in medications:
        db.session.add(Medication(**medication))
    db.session.commit()

    # Seed PharmacyStock
    pharmacy_stock = [
        {'medication_id': 1, 'quantity': 100, 'last_updated': datetime.now(timezone.utc)},
        {'medication_id': 2, 'quantity': 50, 'last_updated': datetime.now(timezone.utc)},
    ]
    for stock in pharmacy_stock:
        db.session.add(PharmacyStock(**stock))

    # Seed PharmacyOrders
    pharmacy_orders = [
        {'medication_id': 1, 'quantity': 50, 'ordered_by': 2, 'order_date': datetime.now(timezone.utc), 'status': 'Pending'},
        {'medication_id': 2, 'quantity': 20, 'ordered_by': 2, 'order_date': datetime.now(timezone.utc), 'status': 'Completed'},
    ]
    for order in pharmacy_orders:
        db.session.add(PharmacyOrder(**order))

    # Seed Schedules
    schedules = [
        {'user_id': 2, 'start_time': datetime.strptime('2025-07-20T08:00:00', '%Y-%m-%dT%H:%M:%S'), 'end_time': datetime.strptime('2025-07-20T16:00:00', '%Y-%m-%dT%H:%M:%S'), 'shift_type': 'Day'},
        {'user_id': 3, 'start_time': datetime.strptime('2025-07-20T08:00:00', '%Y-%m-%dT%H:%M:%S'), 'end_time': datetime.strptime('2025-07-20T16:00:00', '%Y-%m-%dT%H:%M:%S'), 'shift_type': 'Day'},
    ]
    for schedule in schedules:
        db.session.add(Schedule(**schedule))

    # Seed Attendance
    attendance = [
        {'user_id': 2, 'date': datetime.strptime('2025-07-20', '%Y-%m-%d').date(), 'status': 'Present'},
        {'user_id': 3, 'date': datetime.strptime('2025-07-20', '%Y-%m-%d').date(), 'status': 'Present'},
    ]
    for record in attendance:
        db.session.add(Attendance(**record))

    # Seed Payroll
    payroll = [
        {'user_id': 2, 'salary': 5000.00, 'bonus': 500.00, 'deductions': 200.00, 'period_start': datetime.strptime('2025-07-01', '%Y-%m-%d').date(), 'period_end': datetime.strptime('2025-07-31', '%Y-%m-%d').date()},
        {'user_id': 3, 'salary': 4000.00, 'bonus': 300.00, 'deductions': 150.00, 'period_start': datetime.strptime('2025-07-01', '%Y-%m-%d').date(), 'period_end': datetime.strptime('2025-07-31', '%Y-%m-%d').date()},
    ]
    for record in payroll:
        db.session.add(Payroll(**record))

    # Seed Notifications
    notifications = [
        {'user_id': 2, 'message': 'Shift reminder: 08:00 tomorrow', 'sent_at': datetime.now(timezone.utc), 'status': 'Pending'},
        {'user_id': 3, 'message': 'New patient assigned', 'sent_at': datetime.now(timezone.utc), 'status': 'Sent'},
    ]
    for notification in notifications:
        db.session.add(Notification(**notification))

    # Seed AuditLogs
    audit_logs = [
        {'action': 'User registered', 'user': 'admin', 'timestamp': datetime.now(timezone.utc)},
        {'action': 'Patient added', 'user': 'admin', 'timestamp': datetime.now(timezone.utc)},
        {'action': 'Appointment scheduled', 'user': 'admin', 'timestamp': datetime.now(timezone.utc)},
    ]
    for log in audit_logs:
        db.session.add(AuditLog(**log))

    # Seed ErrorLogs
    error_logs = [
        {'error_message': 'Failed to process report', 'user_id': 1, 'timestamp': datetime.now(timezone.utc)},
        {'error_message': 'Invalid input in patient form', 'timestamp': datetime.now(timezone.utc)},
    ]
    for log in error_logs:
        db.session.add(ErrorLog(**log))

    # Seed ReportsGenerated
    reports_generated = [
        {'report_name': 'Patient Summary', 'generated_by': 1, 'generated_at': datetime.now(timezone.utc)},
        {'report_name': 'Inventory Report', 'generated_by': 4, 'generated_at': datetime.now(timezone.utc)},
    ]
    for report in reports_generated:
        db.session.add(ReportsGenerated(**report))

    # Seed BedAllocations
    bed_allocations = [
        {'bed_id': 2, 'patient_id': 1, 'allocation_date': datetime.now(timezone.utc)},
    ]
    for allocation in bed_allocations:
        db.session.add(BedAllocation(**allocation))

    # Seed Equipment
    equipment = [
        {'name': 'Defibrillator', 'status': 'Operational', 'maintenance_date': datetime.strptime('2025-06-01', '%Y-%m-%d').date(), 'created_at': datetime.now(timezone.utc)},
        {'name': 'Ventilator', 'status': 'Maintenance', 'created_at': datetime.now(timezone.utc)},
    ]
    for item in equipment:
        db.session.add(Equipment(**item))

    # Seed SuppliesInventory
    supplies_inventory = [
        {'item_name': 'Gloves', 'quantity': 1000, 'last_updated': datetime.now(timezone.utc)},
        {'item_name': 'Syringes', 'quantity': 500, 'last_updated': datetime.now(timezone.utc)},
    ]
    for item in supplies_inventory:
        db.session.add(SuppliesInventory(**item))

    # Seed Vendors
    vendors = [
        {'name': 'MedSupply Co', 'contact': '1234567899', 'address': '789 Industrial Rd'},
        {'name': 'PharmaCorp', 'contact': '9876543210', 'address': '456 Supply St'},
    ]
    for vendor in vendors:
        db.session.add(Vendor(**vendor))

    # Seed PatientLogins
    patient_logins = [
        {'patient_id': 1, 'username': 'johndoe', 'password': generate_password_hash('patient123')},
        {'patient_id': 2, 'username': 'janesmith', 'password': generate_password_hash('patient123')},
    ]
    for login in patient_logins:
        db.session.add(PatientLogin(**login))

    # Seed PatientFeedback
    patient_feedback = [
        {'patient_id': 1, 'feedback': 'Great service', 'submitted_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'feedback': 'Long wait time', 'submitted_at': datetime.now(timezone.utc)},
    ]
    for feedback in patient_feedback:
        db.session.add(PatientFeedback(**feedback))

    # Seed Downloads
    downloads = [
        {'patient_id': 1, 'document_name': 'Lab_Result_001.pdf', 'downloaded_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'document_name': 'Prescription_002.pdf', 'downloaded_at': datetime.now(timezone.utc)},
    ]
    for download in downloads:
        db.session.add(Download(**download))

    # Seed AppointmentRequests
    appointment_requests = [
        {'patient_id': 1, 'requested_time': datetime.strptime('2025-07-22T09:00:00', '%Y-%m-%dT%H:%M:%S'), 'status': 'Pending', 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'requested_time': datetime.strptime('2025-07-23T11:00:00', '%Y-%m-%dT%H:%M:%S'), 'status': 'Approved', 'created_at': datetime.now(timezone.utc)},
    ]
    for request in appointment_requests:
        db.session.add(AppointmentRequest(**request))

    # Seed Bills
    bills = [
        {'patient_id': 1, 'amount': 100.00, 'description': 'Consultation fee', 'payment_status': 'Pending', 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'amount': 150.00, 'description': 'Checkup fee', 'payment_status': 'Paid', 'created_at': datetime.now(timezone.utc)},
    ]
    for bill in bills:
        db.session.add(Bill(**bill))

    # Seed SecurityLogs
    security_logs = [
        {'event': 'Login attempt', 'user': 'admin', 'status': 'Success', 'timestamp': datetime.now(timezone.utc)},
        {'event': 'Login attempt', 'user': 'unknown', 'status': 'Failed', 'timestamp': datetime.now(timezone.utc)},
    ]
    for log in security_logs:
        db.session.add(SecurityLog(**log))

    # Seed LabSamples
    lab_samples = [
        {'patient_id': 1, 'sample_type': 'Blood', 'collection_time': datetime.now(timezone.utc), 'collected_by': 5, 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'sample_type': 'Urine', 'collection_time': datetime.now(timezone.utc), 'collected_by': 5, 'created_at': datetime.now(timezone.utc)},
    ]
    for sample in lab_samples:
        db.session.add(LabSample(**sample))

    # Seed Vitals
    vitals = [
        {'patient_id': 1, 'blood_pressure': '120/80', 'temperature': 36.6, 'pulse': 80, 'respiration': 16, 'recorded_by': 3, 'recorded_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'blood_pressure': '118/78', 'temperature': 37.0, 'pulse': 75, 'respiration': 18, 'recorded_by': 3, 'recorded_at': datetime.now(timezone.utc)},
    ]
    for vital in vitals:
        db.session.add(Vitals(**vital))

    # Seed Communication Settings
    communication_settings = [
        {'sms': True, 'email': True, 'chat': False, 'updated_at': datetime.now(timezone.utc)},
    ]
    for setting in communication_settings:
        db.session.add(Communication(**setting))

    # Seed LabOrders
    lab_orders = [
        {'patient_id': 1, 'test_type': 'CBC', 'status': 'Pending', 'created_by': 2, 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'test_type': 'Urinalysis', 'status': 'Completed', 'created_by': 2, 'created_at': datetime.now(timezone.utc)},
    ]
    for order in lab_orders:
        db.session.add(LabOrder(**order))

    # Seed RadiologyOrders
    radiology_orders = [
        {'patient_id': 1, 'test_type': 'X-Ray', 'status': 'Pending', 'created_by': 2, 'created_at': datetime.now(timezone.utc)},
        {'patient_id': 2, 'test_type': 'MRI', 'status': 'Scheduled', 'created_by': 2, 'created_at': datetime.now(timezone.utc)},
    ]
    for order in radiology_orders:
        db.session.add(RadiologyOrder(**order))

    db.session.commit()
    print("Database seeded successfully")