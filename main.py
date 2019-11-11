#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 18:33:56 2019

@author: tech
"""
from collections import namedtuple
import json
from os.path import exists
import sys

from elasticsearch_dsl.query import Ids, MultiMatch
from elasticsearch_dsl import connections, Search

from flask import Flask, render_template, g, session, redirect, url_for, jsonify, abort
from flask_wtf import FlaskForm
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

Config = namedtuple('Config', ['username', 'password', 'secret', 'hosts',
                               'index', 'database', 'collection'])
CONFIG = 'config.json'

def read_config():
    if exists(CONFIG):
        with open(CONFIG) as config:
            conf = json.load(config)
    else:
        print("Could not find configuration file {0}.".format(CONFIG))
        sys.exit(1)
    
    return Config(
        username = conf['username'],
        password = conf['password'],
        secret = conf['secret_key'],
        hosts = conf['es_hosts'],
        index = conf['index'],
        database = conf['database'],
        collection = conf['collection']
    )
    
config = read_config()
conn = connections.create_connection(hosts=config.hosts)
search = Search(using=conn)
search = search.index('library')

arangoconn = Connection(username = config.username, password = config.password)
db = arangoconn[config.database]

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret

class NameForm(FlaskForm):
    name = StringField('What is your query?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class PageButton(FlaskForm):
    button = SubmitField()
    

class SortForm(FlaskForm):
    order = SelectField(label='Sort order', choices=[("desc", "newest first"),
                                                     ("asc", "oldest first")])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['query'] = form.name.data
        session['from_hit'] = 0
        session['to_hit'] = 10
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
    if form.validate_on_submit(): # wird suchbutton geklickt wird neue suche gespeichert
        session['query'] = form.name.data
        session['from_hit'] = 0
        session['to_hit'] = 10
        return redirect(url_for('results'))
    else: # andernfalls wird seite angezeigt
        prepared_search = search.query(Ids(values=id))
        results = prepared_search.execute()
        if len(results.hits) == 0:
            abort(404)
        hit = results.hits[0]
        try:
            db[config.collection][id]
            pdfexists = True
        except DocumentNotFoundError:
            pdfexists = False
        return render_template('page.html', form=form, hit=hit,pdfexists=pdfexists,pdf=pdf)
    # es wird alles angezeigt, was als hit übergeben wird, mit entry: davor


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


@app.route('/results', methods=['GET', 'POST'])
def results():
    form = NameForm()
    backwards = PageButton()
    forwards = PageButton()
    sort_form = SortForm()
    if form.validate_on_submit():
        session['query'] = form.name.data
        return redirect(url_for('results'))
    else:
        form.name.data = session['query']
        execute_query(form.name.data)
    return render_template('results.html', form=form, query=session.get('query'),
                           hits=g.get('hits'), time=session.get('time'),
                           total_hits=session.get('total_hits'),
                           _from=session['from_hit'], _to=session['to_hit'],
                           backwards=backwards, forwards=forwards,
                           sort_form=sort_form)


def execute_query(data):
    prepared_search = search.sort({"year": {"order": "desc"}})
    prepared_search = prepared_search.query(MultiMatch(query=data))
    hits = []
    from_hit = session['from_hit']
    to_hit = session['to_hit']
    results = prepared_search[from_hit:to_hit].execute()
    if results.hits.total.value != 0:
        for r in results:
            hit = {'id': r.meta.id}
            if 'title' in r:
                hit['title'] = r.title
            if 'author' in r:
                hit['author'] = " and ".join(r.author)
            if 'abstract' in r:
                hit['abstract'] = r.abstract
            hits.append(hit)

    g.hits = hits
    session['time'] = str(results.took)
    session['total_hits'] = str(results.hits.total.value)
