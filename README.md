# hmis-backend
HMIS Backend
Hospital Management Information System backend built with Flask and PostgreSQL.
Setup

Clone the repository:git clone https://github.com/<your-username>/hmis-backend.git
cd hmis-backend


Set up Python environment:python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Configure PostgreSQL:
Install PostgreSQL and create a database: hmis_db.
Create .env file in the root directory:DATABASE_URL=postgresql://user:password@localhost:5432/hmis_db
FLASK_ENV=development
JWT_SECRET_KEY=your-secret-key




Run migrations:flask db init
flask db migrate
flask db upgrade


Run the app:flask run



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
