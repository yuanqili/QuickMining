from flask import render_template
from flask_mail import Message
from app import mail, app


# Note that Flask-Mail also supports Cc, Bcc, but we don't use here.
def send_mail(subject, sender, recipients, body_text, body_html):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = body_text
    msg.html = body_html
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail('[ModernFlask] Reset your password',
              sender=app.config['ADMINS'][0],
              recipients=[user.email],
              # The templates receive the user and the token as arguments, so
              # that a personalized email message can be generated.
              body_text=render_template('email/reset_password.txt', user=user, token=token),
              body_html=render_template('email/reset_password.html', user=user, token=token))
