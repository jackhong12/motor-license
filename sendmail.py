import smtplib
import markdown
import private 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailHandler:
    def __init__ (self):
        self.content1 = ""
        self.content2 = ""

    def bold (self, msg, isImportant = True):
        if isImportant:
            self.content1 += f"**{msg}**"
        else:
            self.content2 += f"**{msg}**"

    def text (self, msg, isImportant = True):
        if isImportant:
            self.content1 += f"{msg}"
        else:
            self.content2 += f"{msg}"

    def textln (self, msg, isImportant = True):
        if isImportant:
            self.content1 += f"{msg}\n"
        else:
            self.content2 += f"{msg}\n"

    def newParagraph (self, isImportant = True):
        if isImportant:
            self.content1 += "---\n"
        else:
            self.content2 += "---\n"

    def plain (self):
        print(self.content1)
        print(self.content2)

    def send (self):
        fullContent = self.content1 + "\n---\n"
        fullContent += self.content2
        html = markdown.markdown(fullContent)
        self.send_impl(html)

    def send_impl (self, txt, subject="機車路考預約"):
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
