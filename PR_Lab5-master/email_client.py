import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import poplib
import email
import os

class EmailClient:
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, receiver_email, subject, body, attachment_path=None, message_id=None):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg['In-Reply-To'] = message_id

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={attachment_path.split("/")[-1]}')
                msg.attach(part)
            os.remove(attachment_path) # as intended :)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        
        text = msg.as_string()
        
        server.sendmail(self.sender_email, receiver_email, text)
        server.quit()

    def receive_emails(self, protocol='IMAP', limit=None, download_attachments=False):
        if protocol.upper() == 'POP3':
            mail = poplib.POP3_SSL('pop.gmail.com')
            mail.user(self.sender_email)
            mail.pass_(self.sender_password)
            _, message_count_bytes, _ = mail.list()
            messages = [int(msg.split()[0]) for msg in message_count_bytes]  # Extract message numbers as integers
        elif protocol.upper() == 'IMAP':
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.sender_email, self.sender_password)
            mail.select('inbox')
            _, messages = mail.search(None, 'ALL')

        if limit:
            if protocol.upper() != 'IMAP':
                messages = messages[-limit:]
            else:
                messages = messages[0].split()[-limit:]
        
        emails = []
        for num in messages:
            if protocol.upper() == 'POP3':
                _, data, _ = mail.retr(num)
                raw_email = b'\n'.join(data)
            else:
                _, data = mail.fetch(num, '(RFC822)')
                raw_email = data[0][1]

            email_data = self.process_emails(download_attachments, raw_email)
            email_data['Thread-ID'] = self.get_thread_id(raw_email)
            emails.append(email_data)

        if protocol.upper() == 'POP3':
            mail.quit()
        else:
            mail.close()
            mail.logout()
        return emails

    def process_emails(self, download_attachments, raw_email):
        email_message = email.message_from_bytes(raw_email)
        email_data = {
                'From': email_message['From'],
                'Subject': email_message['Subject'],
                'Date': email_message['Date'],
                'Body': '',
                'Attachment': '',
                'Message-ID': email_message['Message-ID']
            }
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                email_data['Body'] = part.get_payload(decode=True).decode('utf-8')
            if part.get_content_type() == "application/octet-stream":
                email_data['Attachment'] = part.get_filename()
                if download_attachments:
                    if not os.path.exists('files'):
                        os.makedirs('files')
                    attachment_data = part.get_payload(decode=True)
                    with open(f"files/{part.get_filename()}", 'wb') as f:
                        f.write(attachment_data)
        return email_data

    def get_thread_id(self, raw_email):
        email_message = email.message_from_bytes(raw_email)
        references = email_message.get_all('References')
        if references:
            for ref in references:
                thread_id = ref.split()[-1].strip("<>")
                return thread_id
        return None

if __name__ == '__main__':
    email = input('email: ')
    password = input('password: ') # app password pentru aplicatiile vechi pe gmail
    client = EmailClient(email, password)
    client.send_email('receiver_email', 'Subject', 'Body', attachment_path=None)
    emails = client.receive_emails(protocol='IMAP', limit=5, download_attachments=True)
    print(emails)