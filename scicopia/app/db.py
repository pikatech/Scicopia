import re
from typing import Dict, List

from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from elasticsearch_dsl import Q
from fastDamerauLevenshtein import damerauLevenshtein
from flask import current_app, flash, g, session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pyArango.theExceptions import DocumentNotFoundError
from werkzeug.security import check_password_hash, generate_password_hash

from .parser.QueryListener import QueryListener
from .parser.ScicopiaLexer import ScicopiaLexer
from .parser.ScicopiaParser import ScicopiaParser


def link(texts: List[str]) -> List[str]:
    URL_MATCHER = current_app.config["URL_MATCHER"]
    parts = []
    for text in texts:
        parts.append(re.subn(URL_MATCHER, r'<a href="\g<0>">\g<0></a>', text)[0])
    return parts


def analyze_input(input: str) -> Dict[str, Dict[str, str]]:
    input_stream = InputStream(input)
    lexer = ScicopiaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ScicopiaParser(stream)
    listener = QueryListener()
    tree = parser.query()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return listener.getQueries()

def checkFields(condition, fields):
    for typ, cond in condition.items(): # one pass
        for field in cond: # one pass
            field = field.lower()
            if field in fields: # field is allowed
                pass # change nothing
            elif field == "query":
                if typ != "multi_match":
                    newcond = condition.pop(typ) # remove old condition
                    if typ == "match_phrase":
                        newcond["type"] = "phrase"
                    condition["multi_match"] = newcond # make sure type is multi_match for query
            else:
                found = False
                for tag in fields:
                    if damerauLevenshtein(field, tag, similarity=False) == 1.0:
                        flash(f"Field '{field}' not found do you mean '{tag}'?")
                        cond[tag] = cond.pop(field)
                        found = True
                        break
                if not found:
                    flash(f"Field '{field}' not found. Field restriction removed.")
                    cond["query"] = cond.pop(field)
                    condition["multi_match"] = condition.pop(typ) # make sure type is multi_match for query
            if "auto_tags" in cond:
                if type(cond["auto_tags"]) == str:
                    cond["auto_tags"] = [cond["auto_tags"]]
                condition["terms"] = condition.pop(typ)
                return condition, cond["auto_tags"][0]
            break
        break
    return condition, False

def newsearch():
    query = []
    for condition in session["condition"]["must"]:
        for typ, cond in condition.items(): # one pass
            for field, value in cond.items(): # one pass
                if field == "auto_tags":
                    query.append(f"{field}: '{value[0]}'")
                else:
                    query.append(f"{field}: '{value}'")
                break
            break
    for condition in session["condition"]["must_not"]:
        for typ, cond in condition.items(): # one pass
            for field, value in cond.items(): # one pass
                if field == "auto_tags":
                    query.append(f"-{field}: '{value[0]}'")
                else:
                    query.append(f"-{field}: '{value}'")
                break
            break
    session["query"] = " ".join(query)

def execute_query():
    conditions = []
    restrictions = []
    # TODO: flash nur kurz (noch keine möglichkeit gefunden)
    # TODO: was soll passieren, wenn es keine suche gibt? (in dem fall durch entfernen des autotags als einzige suche)
    # TODO: restriction werden auch den conditions hinzugefügt -> fehler finden und beheben (entferne bisher nur symptom)
    fields = current_app.config["FIELDS"]
    for condition in session["condition"]["must"]:
        condition, autotag = checkFields(condition, fields)
        if autotag:
            session["tags"].append({"name": autotag, "mark": True})
        conditions.append(Q(condition))
    for restriction in session["condition"]["must_not"]:
        restriction, autotag = checkFields(restriction, fields)
        while True: # make sure the restriction is not in the conditions
            if restriction in session["condition"]["must"]:
                flash(f"Found {restriction} in condition and restriction, removed from condition.")
                session["condition"]["must"].remove(restriction)
                conditions.remove(Q(restriction))
            else:
                break
        restrictions.append(Q(restriction))
    newsearch()
    prepared_search = current_app.config["SEARCH"].sort({"year": {"order": "desc"}})
    # TODO: add possibility for asc order
    prepared_search = prepared_search.query(Q({"bool": {"must": conditions}}))
    if restrictions:
        prepared_search = prepared_search.query(Q({"bool": {"must_not": restrictions}}))
    prepared_search = prepared_search.highlight('abstract')
    prepared_search = prepared_search.highlight_options(pre_tags=["<b>"],
                                                        post_tags=["</b>"],
                                                        number_of_fragments=0)
    hits = []
    tags = []
    from_hit = session["from_hit"]
    to_hit = session["to_hit"]
    prepared_search.aggs.bucket("by_tag", "terms", field="auto_tags")
    response = prepared_search[from_hit:to_hit].execute()
    if response.hits.total.value != 0:
        for r in response:
            hit = {"id": r.meta.id}
            if "title" in r:
                hit["title"] = r.title
            if "author" in r:
                hit["author"] = " and ".join(r.author)
            if "highlight" in r.meta and "abstract" in r.meta.highlight:
                hit["abstract"] = link(r.meta.highlight.abstract)
            elif "abstract" in r:
                hit["abstract"] = link(r.abstract)
                
            hits.append(hit)
        for item in response.aggregations.by_tag.buckets:
            tag = {"name": item.key, "nr": item.doc_count, "mark": False}
            if next(
                (
                    item
                    for item in session["tags"]
                    if item["name"] == tag["name"] and item["mark"]
                ),
                False,
            ):
                tag.update({"mark": True})
            tags.append(tag)

    g.hits = hits
    session["showfulltext"] = False
    session["tags"] = tags
    session["time"] = str(response.took)
    session["total_hits"] = response.hits.total.value


def add_search(data):
    try:
        search = current_app.config["USERCOLLECTION"][session["user"]]["lastsearch"]
    except:
        flash(f"User key {session['user']} not found, remove user from session")
        session["user"] = None
        return
    if data in search:
        search.remove(data)
    search.append(data)
    if len(search) >= 6:
        search = search[1:]
    doc = current_app.config["USERCOLLECTION"][session["user"]]
    doc["lastsearch"] = search
    doc.save()


def verify_password(user, password):
    return check_password_hash(
        current_app.config["USERCOLLECTION"][user]["password_hash"], password
    )


def reset_password(token, new_password):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token.encode("utf-8"))
    except:
        return False
    try:
        doc = current_app.config["USERCOLLECTION"][data.get("confirm")]
        userexists = True
    except DocumentNotFoundError:
        userexists = False
    if not userexists:
        return False
    doc["password_hash"] = generate_password_hash(new_password)
    doc.save()
    return True


def generate_confirmation_token(user, expiration=3600):
    s = Serializer(current_app.config["SECRET_KEY"], expiration)
    return s.dumps({"confirm": user}).decode("utf-8")


def confirm_u(user, token):
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token.encode("utf-8"))
    except:
        return False
    if data.get("confirm") != user:
        return False
    doc = current_app.config["USERCOLLECTION"][user]
    doc["confirmed"] = True
    doc.save()
    return True
