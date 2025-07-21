# hmis-backend
HMIS Backend
Hospital Management Information System backend built with Flask and PostgreSQL.
## Setup

### Quick Setup (Recommended)
Run the automated setup script:
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. **Clone the repository:**
```bash
git clone https://github.com/<your-username>/hmis-backend.git
cd hmis-backend
```

2. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment:**
Create `.env` file in the root directory:
```env
DATABASE_URL=sqlite:///hmis.db
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-secret-key
```

4. **Run migrations:**
```bash
export FLASK_APP=app.py
flask db upgrade
```

5. **Seed database:**
```bash
python seed.py
```

6. **Run the app:**
```bash
flask run
```

### Test Users
After seeding, you can login with these test accounts:
- **Admin**: username=`admin`, password=`password123`
- **Doctor**: username=`doctor1`, password=`password123`  
- **Nurse**: username=`nurse1`, password=`password123`
- **IT**: username=`it1`, password=`password123`
- **Lab Tech**: username=`labtech1`, password=`password123`



Testing

Run Pytest:pytest



Deployment

Deployed on Heroku: <your-heroku-app>.herokuapp.com.
Push changes to main branch to trigger GitHub Actions deployment.

API Endpoints

/api/register: POST (create user)
/api/login: POST (login, returns JWT)
/api/patients: GET (list patients, paginated), POST (add patient)
/api/patients/<id>: GET (view patient), PUT (update patient)
/api/appointments: GET (list appointments, paginated), POST (schedule appointment)
/api/records: POST (add medical record)
/api/bills: POST (generate invoice), PUT (update payment status)
