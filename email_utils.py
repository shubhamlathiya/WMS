from flask_mail import Mail, Message
from flask import current_app

# Initialize the mail object
mail = Mail()

def send_email(subject, recipient_email, body):
    try:
        msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[recipient_email])
        msg.body = body

        # Send the email
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
