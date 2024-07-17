import unittest
import os
import tempfile
from app import app

class PDFReaderTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_index(self):
        rv = self.client.get('/')
        self.assertIn(b'<title>Welcome to PDF Reader</title>', rv.data)

    def test_login(self):
        rv = self.client.post('/authenticate', data=dict(
            username='abc@gmail.com',
            password='123'
        ))
        self.assertIn(b'PDF Reader', rv.data)

    def test_register(self):
        rv = self.client.post('/register', data=dict(
            username='newuser',
            password='newpassword'
        ))
        self.assertIn(b'Registered successfully!', rv.data)

    def test_upload_pdf(self):
        with open('test.pdf', 'rb') as pdf:
            rv = self.client.post('/upload_pdf', data=dict(
                file=(pdf, 'test.pdf')
            ))
        self.assertIn(b'PDF uploaded successfully', rv.data)

    def test_ask_pdf(self):
        # First, upload a PDF
        with open('test.pdf', 'rb') as pdf:
            self.client.post('/upload_pdf', data=dict(
                file=(pdf, 'test.pdf')
            ))
        # Then, ask a question
        rv = self.client.post('/ask_pdf', json=dict(
            question='What is the content of the PDF?'
        ))
        self.assertIn(b'Hello dear user, how can I assist you today?', rv.data)

if __name__ == '__main__':
    unittest.main()


