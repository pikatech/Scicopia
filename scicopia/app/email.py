from threading import Thread

from flask import current_app, render_template
from flask_mailman import Message

from . import mail


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
        sender=app.config["MAIL_SENDER"],
        recipients=[to],
    )
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg) # flask_mailman doesn't send in testing mode
        if app.testing: # writes only to hard disk, if in testing mode
            with open("email.txt", "wt", encoding="utf-8") as out:
                out.write(str(msg))
