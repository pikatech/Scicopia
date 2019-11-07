#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 18:33:56 2019

@author: tech
"""
import json
from os.path import exists
import sys

from elasticsearch_dsl.query import Ids, MultiMatch
from elasticsearch_dsl import connections, Search

from flask import Flask, render_template, g, session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from pyArango.connection import Connection
from pyArango.theExceptions import DocumentNotFoundError
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

CONFIG = 'config.json'

conn = connections.create_connection(hosts=['localhost'])
search = Search(using=conn)
search = search.index('library')

if exists(CONFIG):
    with open(CONFIG) as config:
        conf = json.load(config)
else:
    print("Could not find configuration file {0}.".format(CONFIG))
    sys.exit(1)

username = conf['username']
password = conf['password']
secret = conf['secret_key']
database = conf['database']
collection = conf['collection']

arangoconn = Connection(username = username, password = password)
db = arangoconn[database]

app = Flask(__name__)
app.config['SECRET_KEY'] = secret

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
        for r in results:
            #TODO: anpassung zum auslesen aller und abhängig vom typ nötig
            # hit = r # reihenfolge von hinzufügen in datenbank bestimmt
            # zeigt auch entrytype an, falls dieser vorhanden
            hit = {'id': r.meta.id} # wollen wir das wirklich anzeigen?
            if 'entrytype' in r:
                hit['entrytype'] = r.entrytype
            if 'author' in r: # festgelegte Reihenfolge und Felder, aber aufwändiger
                hit['author'] = " and ".join(r.author)
            if 'editor' in r:
                hit['editor'] = " and ".join(r.editor)
            if 'publisher' in r:
                hit['publisher'] = r.publisher
            if 'institution' in r:
                hit['institution'] = r.institution
            if 'title' in r:
                hit['title'] = r.title
            if 'title_suggest' in r:
                hit['title_suggest'] = r.title_suggest
            if 'booktitle' in r:
                hit['booktitle'] = r.booktitle
            if 'abstract' in r:
                hit['abstract'] = r.abstract
            if 'keywords' in r:
                hit['keywords'] = r.keywords
            if 'auto_tags' in r:
                hit['auto_tags'] = r.auto_tags
            if 'year' in r:
                hit['year'] = r.year
            if 'pages' in r:
                hit['pages'] = r.pages
            if 'journal' in r:
                hit['journal'] = r.journal
            if 'volume' in r:
                hit['volume'] = r.volume
            if 'number' in r:
                hit['number'] = r.number
            if 'doi' in r:
                hit['doi'] = r.doi
            if 'cited_by' in r:
                hit['cited_by'] = r.cited_by
            if 'citing' in r:
                hit['citing'] = r.citing
            if 'created_at' in r:
                hit['created_at'] = r.created_at
        try:
            db[collection][id]
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
