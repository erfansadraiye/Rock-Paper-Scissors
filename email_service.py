import smtplib, ssl
import time

class EmailService:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.emails = []

    def add_email(self, receiver_email, subject, message):
        self.emails.append((receiver_email, subject, message))

    def clear_emails(self):
        self.emails = []

    def send_email(self):
        server = None
        try:
            server = smtplib.SMTP_SSL("mail.sharif.edu", 465, context=ssl.create_default_context())
            server.login(self.email, self.password)
        except Exception as e:
            print(e)
        try:
            if server is None:
                print('could not loging to email')
                return
            for i, email in enumerate(self.emails):
                msg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( self.email, email[0], email[1], email[2])
                server.sendmail(self.email, email[0], msg)
                print('ok the email has been sent')
        except Exception as e:
            print(e)