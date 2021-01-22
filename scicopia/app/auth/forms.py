from flask_wtf import FlaskForm
from flask import current_app
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

class LoginForm(FlaskForm):
    user = StringField("Username", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or " "underscores",
            ),
        ],
    )
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_username(self, field):
        aql = f"FOR x IN {current_app.config['USERCOLLECTIONNAME']} FILTER x.username == '{field.data}' RETURN x._key"
        queryResult = current_app.config['DB'].AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError("Username already in use.")

    def validate_email(self, field):
        aql = f"FOR x IN {current_app.config['USERCOLLECTIONNAME']} FILTER x.email == '{field.data.lower()}' RETURN x._key"
        queryResult = current_app.config['DB'].AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError("Email already registered.")


class ChangeUsernameForm(FlaskForm):
    username = StringField("New Username", validators=[DataRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Username")

    def validate_username(self, field):
        aql = f"FOR x IN {current_app.config['USERCOLLECTIONNAME']} FILTER x.username == '{field.data}' RETURN x._key"
        queryResult = current_app.config['DB'].AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError("Username already in use.")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm new password", validators=[DataRequired()])
    submit = SubmitField("Update Password")


class PasswordResetRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField(
        "New Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        aql = f"FOR x IN {current_app.config['USERCOLLECTIONNAME']} FILTER x.email == '{field.data.lower()}' RETURN x._key"
        queryResult = current_app.config['DB'].AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError("Email already registered.")

