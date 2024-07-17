from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import PyPDF2
from openai import OpenAI

# Initialize OpenAI client (replace with actual endpoint and key if necessary)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.expanduser('~/uploads')

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_with_bot():
    data = request.json
    user_input = data.get('user_input', '')
    
    if user_input.lower() in ["exit", "quit"]:
        return jsonify({"response": "Goodbye!"})
    
    if 'messages' not in app.config:
        app.config['messages'] = [
            {"role": "system", "content": "You are a helpful assistant who reads pdf's and you will answer questions based on the pdf and you will also get the conversation history to be context aware!."}
        ]
    
    app.config['messages'].append({"role": "user", "content": user_input})
    
    # Ensure PDF text is loaded
    if 'pdf_text' not in app.config:
        return jsonify({"error": "No PDF uploaded. Please upload a PDF first."})
    
    pdf_text = app.config['pdf_text']
    
    # Include PDF content in the messages
    messages_with_pdf = app.config['messages'] + [
        {"role": "user", "content": f"PDF content: {pdf_text}"}
    ]
    
    completion = client.chat.completions.create(
        model="AshanGimhana/llama2-model-gguf-AGL-V2",
        messages=messages_with_pdf,
        temperature=0.7,
    )
    
    bot_response = completion.choices[0].message.content
    app.config['messages'].append({"role": "assistant", "content": bot_response})
    
    return jsonify({"response": bot_response})

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
        app.config['pdf_text'] = text  # Store the extracted text in the app config
        
        return jsonify({"text": text, "message": "File received and processed."})
    
    return jsonify({"error": "Invalid file format. Only PDFs are allowed."})

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

@app.route('/ask_pdf', methods=['POST'])
def ask_pdf():
    data = request.json
    question = data.get('question', '')
    
    if not question or 'pdf_text' not in app.config:
        return jsonify({"error": "Question and PDF text are required."})
    
    pdf_text = app.config['pdf_text']
    
    # Include PDF content in the messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant who reads pdf's and you will answer questions based on the pdf and you will also get the conversation history to be context aware!."},
        {"role": "user", "content": f"PDF content: {pdf_text}"},
        {"role": "user", "content": question}
    ]
    
    completion = client.chat.completions.create(
        model="AshanGimhana/llama2-model-gguf-AGL-V2",
        messages=messages,
        temperature=0.7,
    )
    
    bot_response = completion.choices[0].message.content
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)