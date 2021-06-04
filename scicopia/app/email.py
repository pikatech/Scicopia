from threading import Thread

from flask import current_app, render_template
from flask_mailman import EmailMultiAlternatives

from . import mail


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = EmailMultiAlternatives(
        subject=app.config["MAIL_SUBJECT_PREFIX"] + " " + subject,
        body = render_template(template + ".txt", **kwargs),
        from_email=app.config["MAIL_SENDER"],
        to=[to],
    )
    html_content = render_template(template + ".html", **kwargs)
    msg.attach_alternative(html_content, "text/html")
    msg.send() # flask_mailman doesn't send in testing mode
    if app.testing:  # writes only to hard disk, if in testing mode
        with open("email.txt", "wt", encoding="utf-8") as out:
            out.write(msg.body)
