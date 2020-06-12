import re
from typing import List, Dict
from pyArango.theExceptions import DocumentNotFoundError
from elasticsearch_dsl import Q
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import g, session, current_app

from antlr4 import CommonTokenStream, InputStream, ParseTreeWalker
from .parser.ScicopiaLexer import ScicopiaLexer
from .parser.QueryListener import QueryListener
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


def execute_query():
    conditions = []
    restrictions = []
    for condition in session["condition"]["must"]:
        conditions.append(Q(condition))
    for restriction in session["condition"]["must_not"]:
        restrictions.append(Q(condition))
    prepared_search = current_app.config["SEARCH"].sort({"year": {"order": "desc"}})
    prepared_search = prepared_search.query(Q({"bool": {"must": conditions}}))
    if restrictions:
        prepared_search = prepared_search.query(Q({"bool": {"must_not": conditions}}))
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
    session["tags"] = tags
    session["time"] = str(response.took)
    session["total_hits"] = response.hits.total.value


def add_search(data):
    search = current_app.config["USERCOLLECTION"][session["user"]]["lastsearch"]
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
