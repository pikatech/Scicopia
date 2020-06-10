from pyArango.theExceptions import DocumentNotFoundError, CreationError
from elasticsearch_dsl import Q
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import g, session, current_app


def execute_query():
    conditions = []
    for condition in session["condition"]:
        conditions.append(Q(condition))
    prepared_search = current_app.config["SEARCH"].sort({"year": {"order": "desc"}})
    prepared_search = prepared_search.query(Q({"bool": {"must": conditions}}))
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
                hit["abstract"] = r.meta.highlight.abstract                
            elif "abstract" in r:
#                 abstractparts = []
#                 for abstract in r.abstract:
#                     data = session["query"]
#                     dataparts = current_app.config["NLP"](data)
#                     for data in dataparts:
#                         data = data.text
#                         if data.lower() in abstract.lower() and len(data) > 1:
# #                            abstract = abstract.lower()
# #                            abstract = abstract.replace(
# #                                data.lower(), f"<b>{data.lower()}</b>"
# #                            )
#                             match = current_app.config["URL_MATCHER"].search(abstract)
#                             if match is None:
#                                 abstractparts.append(abstract)
#                             # This will only match the first hit
#                             else:
#                                 abstractparts.append(
#                                     f'{abstract[: match.start()]}<a href="{match.group(0)}">{match.group(0)}</a>{abstract[match.end(): ]}'
#                                 )
#                hit["abstract"] = abstractparts
                hit["abstract"] = r.abstract
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
