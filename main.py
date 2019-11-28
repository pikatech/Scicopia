#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 18:33:56 2019

@author: tech
"""
import base64
import re
import os
from threading import Thread

from elasticsearch_dsl.query import Ids, MultiMatch
from elasticsearch_dsl import connections, Search, Q
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError, CreationError

from flask import (Flask, render_template, g, session, redirect, url_for,
                   make_response, jsonify, abort, flash, request, 
                   current_app)
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from wtforms import (StringField, SubmitField, SelectField, PasswordField, 
                    BooleanField, ValidationError)
from wtforms.validators import (DataRequired, Length, Email, Regexp, 
                                EqualTo)

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from config import read_config

config = read_config()
conn = connections.create_connection(hosts=config.hosts)
search = Search(using=conn)
search = search.index(config.index)

arangoconn = Connection(username = config.username, password = config.password)
db = arangoconn[config.database]

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = config.mailusername
app.config['MAIL_PASSWORD'] = config.mailpassword
app.config['Scicopia_MAIL_SUBJECT_PREFIX'] = '[Scicopia]'
app.config['Scicopia_MAIL_SENDER'] = 'Scicopia Admin'

bootstrap = Bootstrap(app)
mail = Mail(app)

url_matcher = re.compile(r'https?://\w+(\.\w+)+(/\w+)+([-.,_]\w+)*(#\w+)?')

class NameForm(FlaskForm):
    name = StringField('What is your query?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PageButton(FlaskForm):
    button = SubmitField()
    

class SortForm(FlaskForm):
    order = SelectField(label='Sort order', choices=[("desc", "newest first"),
                                                     ("asc", "oldest first")])


class LoginForm(FlaskForm):
    user = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, field):
        aql = "FOR x IN'" + config.usercollection + "'FILTER x.username == '" + field.data.lower() + "' RETURN x._key"
        queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        aql = "FOR x IN'" + config.usercollection + "'FILTER x.email == '"+field.data.lower()+"' RETURN x._key"
        queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError('Email already registered.')


class ChangeUsernameForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Username')

    def validate_username(self, field):
        aql = "FOR x IN'" + config.usercollection + "'FILTER x.username == '"+field.data.lower()+"' RETURN x._key"
        queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        aql = "FOR x IN'" + config.usercollection + "'FILTER x.email == '"+field.data.lower()+"' RETURN x._key"
        queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            raise ValidationError('Email already registered.')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if not 'user' in session:
        session['user'] = None
        session['next'] = None
    if form.validate_on_submit():
        session['query'] = form.name.data
        session['from_hit'] = 0
        session['to_hit'] = 10
        session['tags'] = []
        return redirect(url_for('results'))
    return render_template('index.html', form=form)


@app.route('/total', methods=['GET', 'POST'])
def total():
    prepared_search = search.query(MultiMatch(query=session['query']))
    results = prepared_search.execute()
    return jsonify({"total": str(results.hits.total.value)})


@app.route('/page/<id>', methods=['GET', 'POST'])
def page(id):
    form = NameForm()
    pdf = PageButton()
    if form.validate_on_submit():
        session['query'] = form.name.data
        session['from_hit'] = 0
        session['to_hit'] = 10
        return redirect(url_for('results'))
    else:
        prepared_search = search.query(Ids(values=id))
        results = prepared_search.execute()
        if len(results.hits) == 0:
            abort(404) # Macht aus den Fehler 500 ein Fehler 404
        hit = results.hits[0]
        try:
            db[config.collection][id]
            pdfexists = True
        except DocumentNotFoundError:
            pdfexists = False
        return render_template('page.html', form=form, hit=hit, pdfexists=pdfexists, pdf=pdf)


@app.route('/forwards', methods=['GET', 'POST'])
def forwards():
    session['from_hit'] += 10
    session['to_hit'] += 10
    execute_query(session['query'])
    return redirect(url_for('results'))


@app.route('/backwards', methods=['GET', 'POST'])
def backwards():
    session['from_hit'] -= 10
    session['to_hit'] -= 10
    execute_query(session['query'])
    return redirect(url_for('results'))


@app.route('/pdf/<id>', methods=['GET', 'POST'])
def pdf(id):
    coll = db[config.collection]
    data = coll[id]["data"] #! data in pdf umbennen, da später auch die bibdaten in arango sind
    data = base64.b64decode(data)
    response = make_response(data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % (id)
    return response


@app.route('/results', methods=['GET', 'POST'])
def results():
    form = NameForm()
    backwards = PageButton()
    forwards = PageButton()
    sort_form = SortForm()
    if form.validate_on_submit():
        session['query'] = form.name.data
        session['from_hit'] = 0
        session['to_hit'] = 10
        return redirect(url_for('results'))
    else:
        form.name.data = session['query']
        execute_query(form.name.data)
        if session['user'] is not None:
            add_search(session['query'])
    return render_template('results.html', form=form, query=session.get('query'),
                           hits=g.get('hits'), tags=session['tags'],
                           time=session.get('time'),
                           total_hits=session.get('total_hits'),
                           _from=session['from_hit'], _to=session['to_hit'],
                           backwards=backwards, forwards=forwards,
                           sort_form=sort_form)


@app.route('/tags/<tag>')
def tags(tag):
    #mach was auch immer beim anklicken eines tags geschehen soll
    # TODO: hinzufügen des tags zur suche
    for d in session["tags"]:
        if d['name'] == tag:
            if d['mark'] == False:
                d.update({'mark':True})
                flash('%s hinzugefügt'%(tag))
            else:
                d.update({'mark':False})
                flash('%s entfernt' %(tag))
            break
    return redirect(url_for('results'))


@app.route('/oldsearch/<search>')
def oldsearch(search):
    session['query'] = search
    session['from_hit'] = 0
    session['to_hit'] = 10
    return redirect(url_for('results'))


def execute_query(data):
    prepared_search = search.sort({"year": {"order": "desc"}})
    prepared_search = prepared_search.query(MultiMatch(query=data))
    hits = []
    tags = []
    from_hit = session['from_hit']
    to_hit = session['to_hit']
    prepared_search.aggs.bucket('by_tag', 'terms', field='auto_tags')
    results = prepared_search[from_hit:to_hit].execute()
    if results.hits.total.value != 0:
        for r in results:
            hit = {'id': r.meta.id}
            if 'title' in r:
                hit['title'] = r.title
            if 'author' in r:
                hit['author'] = " and ".join(r.author)
            if 'abstract' in r:
                match = url_matcher.search(r.abstract)
                if match is None:
                    hit['abstract'] = r.abstract
                # This will only match the first hit
                else:
                    hit['abstract'] = ('%s<a href="%s">%s</a>%s') % (r.abstract[:match.start()],
                       match.group(0), match.group(0), r.abstract[match.end():])
            hits.append(hit)
        for item in results.aggregations.by_tag.buckets:
            tag = {'name':item.key, 'nr':item.doc_count, 'mark':True}
            if not tag in session['tags']:
                tag.update({'mark':False})
            tags.append(tag)

    g.hits = hits
    session['tags'] = tags
    session['time'] = str(results.took)
    session['total_hits'] = results.hits.total.value


def add_search(data):
    search = db[config.usercollection][session['user']]['lastsearch']
    if data in search:
        search.remove(data)
    search.append(data)
    if len(search) >= 6:
        search = search[1:]
    doc = db[config.usercollection][session['user']]
    doc['lastsearch'] = search
    doc.save()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        aql = "FOR x IN'" + config.usercollection + "'FILTER x.username == '"+username+"' RETURN x._key"
        queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult and verify_password(queryResult[0], form.password.data):
            session['user'] = queryResult[0]
            next = session['next']
            session['next'] = None
            if next is None or not next.startswith('/'):
                next = url_for('unconfirmed')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

def verify_password(user, password):
    return check_password_hash(db[config.usercollection][user]['password_hash'], password)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        doc = db[config.usercollection].createDocument()
        doc['username'] = form.username.data
        doc['email'] = form.email.data.lower()
        doc['password_hash'] = generate_password_hash(form.password.data)
        doc['lastsearch'] = []
        doc['confirmed'] = False
        doc.save()
        token = generate_confirmation_token(doc._key)
        send_email(doc['email'], 'Confirm Your Account',
                   'auth/email/confirm', user=db[config.usercollection][doc._key]['username'], token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if session['user'] is not None:
        session['user'] = None
        flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if session['user'] is not None:
        lastsearch=db[config.usercollection][session['user']]['lastsearch']
        return render_template("auth/profil.html", lastsearch=lastsearch)
    session['next'] = '/profil'
    return redirect(url_for('login'))



@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if session['user'] is not None:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if verify_password(session['user'], form.old_password.data):
                doc = db[config.usercollection][session['user']]
                doc['password_hash'] = generate_password_hash(form.password.data)
                doc.save()
                flash('Your password has been updated.')
                return redirect(url_for('index'))
            else:
                flash('Invalid password.')
        return render_template("auth/change_password.html", form=form)
    session['next'] = '/change-password'
    return redirect(url_for('login'))


@app.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if session['user'] is not None:
        return redirect(url_for('index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        aql = "FOR x IN'" + config.usercollection + "'FILTER x.email == '"+form.email.data.lower()+"' RETURN x._key"
        queryResult = db.AQLQuery(aql, rawResults=True, batchSize=1)
        if queryResult:
            user = queryResult[0]
            token = generate_confirmation_token(user)
            send_email(db[config.usercollection][user]['email'], 'Reset Your Password',
                       'auth/email/reset_password',
                       user=db[config.usercollection][user]['username'], token=token)
            flash('An email with instructions to reset your password has been '
                  'sent to you.')
        else:
            flash('No data found, please contact the serveradmin to reset your password.')
        return redirect(url_for('login'))
    return render_template('auth/reset_password.html', form=form)


@app.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not 'user' in session:
        session['user'] = None
    if session['user'] is not None:
        return redirect(url_for('index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('index'))
    return render_template('auth/reset_password.html', form=form)


def reset_password(token, new_password):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return False
    try:
        doc = db[config.usercollection][data.get('confirm')]
        userexists = True
    except DocumentNotFoundError:
        userexists = False
    if not userexists:
        return False
    doc['password_hash'] = generate_password_hash(new_password)
    doc.save()
    return True


@app.route('/change_username', methods=['GET', 'POST'])
def change_username_request():
    if session['user'] is not None:
        form = ChangeUsernameForm()
        if form.validate_on_submit():
            if verify_password(session['user'], form.password.data):
                doc = db[config.usercollection][session['user']]
                doc['username'] = form.username.data
                doc.save()
                flash('Your username has been updated.')
                return redirect(url_for('index'))
            else:
                flash('Invalid password.')
        return render_template("auth/change_username.html", form=form)
    session['next'] = '/change_username'
    return redirect(url_for('login'))


@app.route('/change_email', methods=['GET', 'POST'])
def change_email_request():
    if session['user'] is not None:
        form = ChangeEmailForm()
        if form.validate_on_submit():
            if verify_password(session['user'], form.password.data):
                new_email = form.email.data.lower()
                doc = db[config.usercollection][session['user']]
                doc['email'] = new_email
                doc['confirmed'] = False
                doc.save()
                token = generate_confirmation_token(session['user'])
                send_email(new_email, 'Confirm your email address',
                        'auth/email/change_email',
                        user=db[config.usercollection][session['user']]['username'], token=token)
                flash('Your email adress has been updated.')
                flash('An email with instructions to confirm your new email '
                    'address has been sent to you.')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password.')
        return render_template("auth/change_email.html", form=form)
    session['next'] = '/change_email'
    return redirect(url_for('login'))


@app.route('/change_email/<token>')
def change_email(token):
    if not 'user' in session:
        session['user'] = None
    if session['user'] is not None:
        if confirm_u(session['user'], token):
            flash('Your new email address has been confirmed.')
        else:
            flash('Invalid request.')
        return redirect(url_for('index'))
    session['next'] = '/change_email/%s' %(token)
    return redirect(url_for('login'))


@app.route('/confirm/<token>')
def confirm(token):
    if not 'user' in session:
        session['user'] = None
    if session['user'] is not None:
        if db[config.usercollection][session['user']]['confirmed']:
            return redirect(url_for('index'))
        if confirm_u(session['user'], token):
            flash('You have confirmed your account. Thanks!')
        else:
            flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('index'))
    session['next'] = '/confirm/%s' %(token)
    return redirect(url_for('login'))


@app.route('/unconfirmed')
def unconfirmed():
    if db[config.usercollection][session['user']]['confirmed']:
        return redirect(url_for('index'))
    return render_template('auth/unconfirmed.html', user=db[config.usercollection][session['user']]['username'])


@app.route('/confirm')
def resend_confirmation():
    if session['user'] is not None:
        token = generate_confirmation_token(session['user'])
        send_email(db[config.usercollection][session['user']]['email'], 'Confirm Your Account',
                'auth/email/confirm', user=db[config.usercollection][session['user']]['username'], token=token)
        flash('A new confirmation email has been sent to you by email.')
        return redirect(url_for('index'))
    session['next'] = '/confirm'
    return redirect(url_for('login'))


def generate_confirmation_token(user, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'confirm': user}).decode('utf-8')


def confirm_u(user, token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token.encode('utf-8'))
    except:
        return False
    if data.get('confirm') != user:
        return False
    doc = db[config.usercollection][user]
    doc['confirmed'] = True
    doc.save()
    return True


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['Scicopia_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['Scicopia_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)