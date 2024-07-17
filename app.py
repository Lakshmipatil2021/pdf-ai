from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.expanduser('~/uploads')

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Dummy user for demonstration (replace with database logic)
users = {'abc@gmail.com': {'username': 'abc@gmail.com', 'password': '123'}}

# Dummy prompt for asking PDF questions
prompt = "You are a helpful assistant who reads PDFs and answers questions based on the PDF and the conversation history."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('pdf_reader'))
    else:
        return "Login Failed. Invalid username or password."

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_user():
    username = request.form.get('username')
    password = request.form.get('password')
    users[username] = {'username': username, 'password': password}
    session['username'] = username
    return redirect(url_for('pdf_reader'))

@app.route('/pdf_reader')
def pdf_reader():
    if 'username' in session:
        return render_template('pdf_reader.html')
    else:
        return redirect(url_for('login'))

@app.route('/ask_pdf', methods=['POST'])
def ask_pdf():
    data = request.json
    user_input = data.get('question', '')

    if 'pdf_text' not in session:
        return jsonify({"error": "No PDF uploaded. Please upload a PDF first."})

    pdf_text = session['pdf_text']

    # Include PDF content and user input in the prompt
    prompt_with_context = f"{prompt}\n\nPDF content: {pdf_text}\n\nUser question: {user_input}"

    # Perform logic to respond based on the PDF content and user input
    # Here, we can implement a response generation based on the prompt and user input
    response = f"Hello dear user, how can I assist you today?"

    return jsonify({"response": response})

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        text = extract_text_from_pdf(file_path)
        session['pdf_text'] = text

        return jsonify({"message": "PDF uploaded successfully"})

def extract_text_from_pdf(file_path):
    # Function to extract text from PDF
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        text = ''
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extract_text()
        return text

if __name__ == '__main__':
    app.run(debug=True)




