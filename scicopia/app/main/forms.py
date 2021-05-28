from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class NameForm(FlaskForm):
    name = StringField("What is your query?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PageButton(FlaskForm):
    button = SubmitField()


class SortForm(FlaskForm):
    order = SelectField(
        label="Sort order",
        choices=[("", "best match"), ("desc", "newest first"), ("asc", "oldest first")],
        validators=[Optional()],
    )
