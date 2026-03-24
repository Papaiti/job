import unittest
import json
from app import app, db, User, Patient
from werkzeug.security import generate_password_hash

class CancerScreeningTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Create a test user
            user = User(username='testclinician', password_hash=generate_password_hash('password123', method='scrypt'))
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def test_registration(self):
        response = self.app.post('/register', data=dict(
            username='newclinician',
            password='password123'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

    def test_login_logout(self):
        response = self.login('testclinician', 'password123')
        self.assertIn(b'Butaro Hospital', response.data)
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Clinician Login', response.data)

    def test_protected_index(self):
        # Accessing index without login should redirect to login
        response = self.app.get('/', follow_redirects=True)
        self.assertIn(b'Clinician Login', response.data)

    def test_prediction_authenticated(self):
        self.login('testclinician', 'password123')
        data = {
            'age': 65,
            'gender': 1,
            'history': 1,
            'smoking': 1,
            'symptoms': 2
        }
        response = self.app.post('/predict', 
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.data)
        self.assertIn('risk_level', res_data)

if __name__ == '__main__':
    unittest.main()
