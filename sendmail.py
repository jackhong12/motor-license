import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECV = os.getenv("EMAIL_RECV")

def sendMails (body, subject="機車有名額時段"):
    # Email configuration
    sender_email = EMAIL_USER 
    password = EMAIL_PASS 
    
    for receiver_email in EMAIL_RECV.split(";"):

        # Compose the email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        # Send the email
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Email sent to {receiver_email} successfully!")
        except Exception as e:
            print(f"Error: {e}")

