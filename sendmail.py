import smtplib
import markdown
import private 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailHandler:
    def __init__ (self):
        self.content = ""

    def bold (self, msg):
        self.content += f"**{msg}**"

    def text (self, msg):
        self.content += f"{msg}"

    def textln (self, msg):
        self.content += f"{msg}\n"

    def newParagraph (self):
        self.content += "---\n"

    def send (self):
        html = markdown.markdown(self.content)
        self.send_impl(html)

    def send_impl (self, txt, subject="機車有名額時段"):
        # Email configuration
        sender_email = private.EMAIL_USER 
        password = private.EMAIL_PASS 
        
        for receiver_email in private.EMAIL_RECV.split(";"):

            # Compose the email
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = subject

            # Add body to email
            message.attach(MIMEText(txt, "html"))

            # Send the email
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                print(f"Email sent to {receiver_email} successfully!")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    mail = MailHandler()
    mail.textln("## Hello")
    mail.textln("- Hello")
    mail.textln("- Hello")
    mail.newParagraph()
    mail.textln("- Hello")
    mail.newParagraph()
    mail.send()
