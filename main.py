#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 18:33:56 2019

@author: tech
"""
from elasticsearch_dsl.query import Ids, MultiMatch
from elasticsearch_dsl import connections, Search

from flask import Flask, render_template, session, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

conn = connections.create_connection(hosts=['localhost'])
search = Search(using=conn)
search = search.index('library')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

class NameForm(FlaskForm):
    name = StringField('What is your query?', validators=[DataRequired()])
    submit = SubmitField('Submit')
    

class SortForm(FlaskForm):
    order = SelectField(label='Sort order', choices=[("desc", "newest first"),
                                                     ("asc", "oldest first")])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session['query'] = form.name.data
        prepared_search = search.sort({"year": {"order": "desc"}})
        prepared_search = prepared_search.query(MultiMatch(query=form.name.data))
        hits = []
        results = prepared_search.execute()
        session['from_hit'] = 0
        session['to_hit'] = 10
#       results = prepared_search[from_hit:to_hit].execute()
        if results.hits.total.value != 0:
            for r in results:
                hit = {'id': r.meta.id}
                if 'title' in r:
                    hit['title'] = r.title
                if 'author' in r:
                    hit['author'] = " and ".join(r.author)
                if 'abstract' in r:
                    hit['abstract'] = r.abstract if len(r.abstract) < 200 else r.abstract[0:197] + "..."
#                if 'year' in r:
#                    hit['year'] = r.year
                hits.append(hit)

        session['hits'] = hits
        session['time'] = str(results.took)
        session['total_hits'] = str(results.hits.total.value)
        return redirect(url_for('results'))
    return render_template('index.html', form=form, query=session.get('query'),
                           hits=session.get('hits'))


@app.route('/total', methods=['GET', 'POST'])
def total():
    prepared_search = search.query(MultiMatch(query=session['query']))
    results = prepared_search.execute()
    return jsonify({"total": str(results.hits.total.value)})


@app.route('/page/{id}', methods=['GET', 'POST'])
def page():
    prepared_search = search.query(Ids(values=id))
    results = prepared_search.execute()
    return jsonify({"total": str(results.hits.total.value)})


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
    sort_form = SortForm()
    if form.validate_on_submit():
        session['query'] = form.name.data
        execute_query(form.name.data)
        return redirect(url_for('results'))
    else:
        form.name.data = session['query']
    return render_template('results.html', form=form, query=session.get('query'),
                           hits=session.get('hits'), time=session.get('time'),
                           total_hits=session.get('total_hits'),
                           _from=session['from_hit'], _to=session['to_hit'],
                           sort_form=sort_form)


def execute_query(data):
    session['query'] = data
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
                hit['abstract'] = r.abstract if len(r.abstract) < 200 else r.abstract[0:197] + "..."
            hits.append(hit)

    session['hits'] = hits
    session['time'] = str(results.took)
    session['total_hits'] = str(results.hits.total.value)
