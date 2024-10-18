import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from decouple import config


def send_email(to_email, subject, body=None, body_html=None):
    name = config('FROM_NAME')
    email = config('FROM_EMAIL')
    from_email = formataddr((name, email))
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    login = config('GOOGLE_APP_LOGIN')
    password = config('GOOGLE_APP_PASSWORD')

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        if body:
            msg.attach(MIMEText(body, 'plain'))
        
        if body_html:
            msg.attach(MIMEText(body_html, 'html'))

        # Connect to the SMTP server and login
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(login, password)
        
        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f'Email sent successfully to {to_email}')

    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')

if __name__ == '__main__':
    # Example usage:
    to_email = 'hello@eyob.tech'
    subject = 'Test Email'
    body = 'This is a test email sent from Python with plain text.'
    
    # Sample HTML content
    body_html = '''
    <html>
      <body>
        <h1>This is an HTML Test Email</h1>
        <p>This is a test email sent from <b>Python Three</b> with HTML formatting.</p>
      </body>
    </html>
    '''
    
    send_email(to_email, subject, body=body, body_html=body_html)
