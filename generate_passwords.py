# hmis-backend/generate_passwords.py
from werkzeug.security import generate_password_hash

passwords = ['password123', 'patient123']
for password in passwords:
    hash = generate_password_hash(password, method='scrypt')
    print(f"Password: {password}, Hash: {hash}")