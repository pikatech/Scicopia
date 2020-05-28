from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)
from . import auth
from .forms import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    PasswordResetRequestForm,
    PasswordResetForm,
    ChangeEmailForm,
    ChangeUsernameForm
)
from ..email import send_email
from ..db import (
    verify_password,
    generate_password_hash,
    generate_confirmation_token,
    reset_password,
    confirm_u
)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        aql = f"FOR x IN {current_app.config['USERCOLLECTIONNAME']} FILTER x.username == '{username}' RETURN x._key"
        queryResult = current_app.config["DB"].AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult and verify_password(queryResult[0], form.password.data):
            session["user"] = queryResult[0]
            next = session["next"]
            session["next"] = None
            if next is None or not next.startswith("/"):
                next = url_for("auth.unconfirmed")
            return redirect(next)
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        doc = current_app.config["USERCOLLECTION"].createDocument()
        doc["username"] = form.username.data
        doc["email"] = form.email.data.lower()
        doc["password_hash"] = generate_password_hash(form.password.data)
        doc["lastsearch"] = []
        doc["confirmed"] = False
        doc.save()
        token = generate_confirmation_token(doc._key)
        send_email(
            doc["email"],
            "Confirm Your Account",
            "auth/email/confirm",
            user=current_app.config["USERCOLLECTION"][doc._key]["username"],
            token=token,
        )
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    if session["user"] is not None:
        session["user"] = None
        flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/profil", methods=["GET", "POST"])
def profil():
    if session["user"] is not None:
        lastsearch = current_app.config["USERCOLLECTION"][session["user"]]["lastsearch"]
        lastsearch.reverse()
        return render_template("auth/profil.html", lastsearch=lastsearch)
    session["next"] = "/profil"
    return redirect(url_for("auth.login"))


@auth.route("/change-password", methods=["GET", "POST"])
def change_password():
    if session["user"] is not None:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if verify_password(session["user"], form.old_password.data):
                doc = current_app.config["USERCOLLECTION"][session["user"]]
                doc["password_hash"] = generate_password_hash(form.password.data)
                doc.save()
                flash("Your password has been updated.")
                return redirect(url_for("main.index"))
            else:
                flash("Invalid password.")
        return render_template("auth/change_password.html", form=form)
    session["next"] = "/change-password"
    return redirect(url_for("auth.login"))


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if session["user"] is not None:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        aql = f"FOR x IN {current_app.config['USERCOLLECTIONNAME']} FILTER x.email == '{form.email.data.lower()}' RETURN x._key"
        queryResult = current_app.config["DB"].AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            user = queryResult[0]
            token = generate_confirmation_token(user)
            send_email(
                current_app.config["USERCOLLECTION"][user]["email"],
                "Reset Your Password",
                "auth/email/reset_password",
                user=current_app.config["USERCOLLECTION"][user]["username"],
                token=token,
            )
            flash(
                "An email with instructions to reset your password has been "
                "sent to you."
            )
        else:
            flash(
                "No data found, please contact the serveradmin to reset your password."
            )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not "user" in session:
        session["user"] = None
    if session["user"] is not None:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if reset_password(token, form.password.data):
            flash("Your password has been updated.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change_username", methods=["GET", "POST"])
def change_username_request():
    if session["user"] is not None:
        form = ChangeUsernameForm()
        if form.validate_on_submit():
            if verify_password(session["user"], form.password.data):
                doc = current_app.config["USERCOLLECTION"][session["user"]]
                doc["username"] = form.username.data
                doc.save()
                flash("Your username has been updated.")
                return redirect(url_for("main.index"))
            else:
                flash("Invalid password.")
        return render_template("auth/change_username.html", form=form)
    session["next"] = "/change_username"
    return redirect(url_for("auth.login"))


@auth.route("/change_email", methods=["GET", "POST"])
def change_email_request():
    if session["user"] is not None:
        form = ChangeEmailForm()
        if form.validate_on_submit():
            if verify_password(session["user"], form.password.data):
                new_email = form.email.data.lower()
                doc = current_app.config["USERCOLLECTION"][session["user"]]
                doc["email"] = new_email
                doc["confirmed"] = False
                doc.save()
                token = generate_confirmation_token(session["user"])
                send_email(
                    new_email,
                    "Confirm your email address",
                    "auth/email/change_email",
                    user=current_app.config["USERCOLLECTION"][session["user"]]["username"],
                    token=token,
                )
                flash("Your email adress has been updated.")
                flash(
                    "An email with instructions to confirm your new email "
                    "address has been sent to you."
                )
                return redirect(url_for("main.index"))
            else:
                flash("Invalid email or password.")
        return render_template("auth/change_email.html", form=form)
    session["next"] = "/change_email"
    return redirect(url_for("auth.login"))


@auth.route("/change_email/<token>")
def change_email(token):
    if not "user" in session:
        session["user"] = None
    if session["user"] is not None:
        if confirm_u(session["user"], token):
            flash("Your new email address has been confirmed.")
        else:
            flash("Invalid request.")
        return redirect(url_for("main.index"))
    session["next"] = f"/change_email/{token}"
    return redirect(url_for("auth.login"))


@auth.route("/confirm/<token>")
def confirm(token):
    if not "user" in session:
        session["user"] = None
    if session["user"] is not None:
        if current_app.config["USERCOLLECTION"][session["user"]]["confirmed"]:
            return redirect(url_for("main.index"))
        if confirm_u(session["user"], token):
            flash("You have confirmed your account. Thanks!")
        else:
            flash("The confirmation link is invalid or has expired.")
        return redirect(url_for("main.index"))
    session["next"] = f"/confirm/{token}"
    return redirect(url_for("auth.login"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_app.config["USERCOLLECTION"][session["user"]]["confirmed"]:
        return redirect(url_for("main.index"))
    return render_template(
        "auth/unconfirmed.html",
        user=current_app.config["USERCOLLECTION"][session["user"]]["username"],
    )


@auth.route("/confirm")
def resend_confirmation():
    if session["user"] is not None:
        token = generate_confirmation_token(session["user"])
        send_email(
            current_app.config["USERCOLLECTION"][session["user"]]["email"],
            "Confirm Your Account",
            "auth/email/confirm",
            user=current_app.config["USERCOLLECTION"][session["user"]]["username"],
            token=token,
        )
        flash("A new confirmation email has been sent to you by email.")
        return redirect(url_for("main.index"))
    session["next"] = "/confirm"
    return redirect(url_for("auth.login"))
