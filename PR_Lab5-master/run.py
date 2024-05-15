from flask import Flask, render_template, request, send_file, send_from_directory
from email_client import EmailClient
import json
import os

app = Flask(__name__)
# uwsv ipzj tifq djud
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        save_login(email, password)
        return render_template('index.html')
    return render_template('auth.html')

@app.route('/list_emails')
def list_emails():
    sender_email, sender_password = load_login()
    client = EmailClient(sender_email, sender_password)
    limit = request.args.get('limit', type=int) or 5
    protocol = request.args.get('protocol', type=str) or 'IMAP'
    protocol = protocol.upper() if protocol.upper() in ['IMAP', 'POP3'] else 'IMAP'
    emails = client.receive_emails(protocol=protocol, limit=limit, download_attachments=True)
    return render_template('list_emails.html', emails=emails)

@app.route('/compose', methods=['GET', 'POST'])
def compose():
    if request.method == 'POST':
        sender_email, sender_password = load_login()
        receiver_email = request.form['recipient']
        subject = request.form['subject']
        body = request.form['body']
        
        if 'attachment' in request.files:
            attachment = request.files['attachment']
            if attachment.filename != '':
                if not os.path.exists('files'):
                    os.makedirs('files')
                attachment_path = f'files/{attachment.filename}'
                attachment.save(f'files/{attachment.filename}')
            else:
                attachment_path = None
        else:
            attachment_path = None

        client = EmailClient(sender_email, sender_password) 
        client.send_email(receiver_email, subject, body, attachment_path)
        return render_template('index.html')
    return render_template('compose.html')

@app.route('/reply_to_email', methods=['GET', 'POST'])
def reply_to_email():
    if request.method == 'POST':
        sender_email, sender_password = load_login()
        thread_id = request.form['thread_id']
        message_id = request.form['Message-ID']
        recipient = request.form['recipient']
        subject = request.form['subject']
       
        body = request.form['body']
        attachment_path = None
        if 'attachment' in request.files:
            attachment = request.files['attachment']
            if attachment.filename != '':
                if not os.path.exists('files'):
                    os.makedirs('files')
                attachment_path = f'files/{attachment.filename}'
                attachment.save(attachment_path)

        client = EmailClient(sender_email, sender_password) 
        client.send_email(recipient, subject, body, attachment_path, message_id=message_id)
        os.remove(attachment_path) if attachment_path else None  
    return "Reply email sent successfully."

@app.route('/download_attachment/<filename>')
def download_attachment(filename):
    if not os.path.exists('files'):
        os.makedirs('files')
    try:
        # return send_file(filename, as_attachment=True) # download by path orice de pe server, top security
        return send_from_directory(directory='files', path=filename, as_attachment=True) # tot asa, dar doar dintrun folder
    except FileNotFoundError:
        return 'File not found'

def save_login(email, password):
    with open("login.json", "w") as json_file:
        data = {"email": email, "pass": password}
        json.dump(data, json_file)

def load_login():
    with open("login.json", "r") as json_file:
        loaded_data = json.load(json_file)
    return loaded_data["email"], loaded_data["pass"]

if __name__ == "__main__":
    app.run(debug=True)