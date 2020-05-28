from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField("What is your query?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PageButton(FlaskForm):
    button = SubmitField()


class SortForm(FlaskForm):
    order = SelectField(
        label="Sort order", choices=[("desc", "newest first"), ("asc", "oldest first")]
    )
