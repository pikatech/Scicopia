import base64
import logging
from typing import Tuple

from elasticsearch_dsl.query import Ids, MultiMatch
from flask import (
    abort,
    current_app,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..db import add_search, analyze_input, execute_query, link
from . import main
from .forms import NameForm, PageButton, SortForm

logger = logging.getLogger("ncbi")


@main.route("/", methods=["GET", "POST"])
def index():
    if not "user" in session:
        session["user"] = None
    if not "next" in session:
        session["next"] = None
    form = NameForm()
    if form.validate_on_submit():
        session["query"] = form.name.data
        session["condition"] = analyze_input(session["query"])
        session["from_hit"] = 0
        session["to_hit"] = 10
        session["tags"] = []
        return redirect(url_for("main.results"))

    return render_template("index.html", form=form)


def split_prefix(string: str) -> Tuple[str, str]:
    """
    Helper function of the autocomplete route.
    Splits the input, so that the auto-completion can work on a window.

    Parameters
    ----------
    string : str
        An input string the user has typed

    Returns
    -------
    Tuple[str, str]
        The first string should be ignored by the auto-completion
        The second string is supposed to be used for auto-completion
    """
    if " " in string:
        if string[-1] == " ":
            try:
                space = string.rindex(" ", 0, -1)
            except ValueError:
                return ("", string)
            else:
                return (string[:space+1], string[space+1:])
        else:
            space = string.rindex(" ")
            try:
                space = string.rindex(" ", 0, space)
            except ValueError:
                return ("", string)
            else:
                return (string[:space+1], string[space+1:])
    else:
        return ("", string)


@main.route("/autocomplete", methods=["POST"])
def autocomplete():
    """
    Query the auto-completion index to retrieve a list of candidates

    Returns
    -------
    List[str] wrapped in JSON
        A list of auto-completion candidates
    """
    text = request.form["prefix"]
    prefix, term = split_prefix(text)
    search = current_app.config["COMPLETION"]
    search = search.index("suggestions")
    search = search.suggest(
        "auto-completion", term, completion={"field": "keywords_suggest", "size": 10}
    )
    results = search.execute()
    if results["timed_out"]:
        logging.warning("Auto-completion request timed out: %s", term)
        return jsonify([])
    hits = results["suggest"]["auto-completion"][0]["options"]
    completions = [hit["text"] for hit in hits]
    return jsonify({"completions": completions, "prefix": prefix, "term": term})


@main.route("/results", methods=["GET", "POST"])
def results():
    if not "user" in session:
        session["user"] = None
    form = NameForm()
    backwards = PageButton()
    forwards = PageButton()
    sort_form = SortForm()
    if form.validate_on_submit():
        session["query"] = form.name.data
        session["condition"] = analyze_input(session["query"])
        session["from_hit"] = 0
        session["to_hit"] = 10
        session["tags"] = []
        return redirect(url_for("main.results"))
    elif sort_form.validate_on_submit():
        if "order" in sort_form.data:
            session["order"] = sort_form.data["order"]
    execute_query()
    form.name.data = session["query"]
    if session["user"] is not None:
        add_search(session["query"])
    return render_template(
        "results.html",
        form=form,
        query=session.get("query"),
        hits=g.get("hits"),
        tags=session["tags"],
        time=session.get("time"),
        total_hits=session.get("total_hits"),
        _from=session["from_hit"],
        _to=session["to_hit"],
        backwards=backwards,
        forwards=forwards,
        sort_form=sort_form,
    )


@main.route("/page/<id>", methods=["GET", "POST"])
def page(id):
    form = NameForm()
    pdf = PageButton()
    ft = PageButton()
    if not "lastpage" in session or not session["lastpage"] == id:
        session["lastpage"] = id
        session["showfulltext"] = False
    if form.validate_on_submit():
        session["query"] = form.name.data
        session["condition"] = analyze_input(session["query"])
        session["from_hit"] = 0
        session["to_hit"] = 10
        session["tags"] = []
        return redirect(url_for("main.results"))
    else:
        prepared_search = current_app.config["SEARCH"].query(Ids(values=id))
        results = prepared_search.execute()
        if len(results.hits) == 0:
            abort(404)
        hit = results.hits[0]
        if "abstract" in hit:
            hit.abstract = link(hit.abstract)
        if "author" in hit:
            hit["author"] = (
                " and ".join(hit.author)
                if len(hit.author) <= 2
                else f"{', '.join(hit.author[:-1])} and {hit.author[-1]}"
            )
        # PDF collection is optional
        pdfexists = (
            id in current_app.config["PDFCOLLECTION"]
            if "PDFCOLLECTION" in current_app.config
            else False
        )
        if session["showfulltext"]:
            fulltext = current_app.config["COLLECTION"][id]["fulltext"]
        else:
            fulltext = "fulltext" in current_app.config["COLLECTION"][id]
        return render_template(
            "page.html",
            form=form,
            hit=hit,
            pdfexists=pdfexists,
            pdf=pdf,
            fulltext=fulltext,
            showfulltext=session["showfulltext"],
            ft=ft,
        )


@main.route("/forwards", methods=["GET", "POST"])
def forwards():
    session["from_hit"] += 10
    session["to_hit"] += 10
    return redirect(url_for("main.results"))


@main.route("/backwards", methods=["GET", "POST"])
def backwards():
    session["from_hit"] -= 10
    session["to_hit"] -= 10
    return redirect(url_for("main.results"))


@main.route("/pdf/<id>", methods=["GET", "POST"])
def pdf(id):
    try:
        data = current_app.config["PDFCOLLECTION"][id]["pdf"]
    except:
        abort(404)
    data = base64.b64decode(data)
    response = make_response(data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={id}.pdf"
    return response


@main.route("/fulltext/<id>", methods=["GET", "POST"])
def fulltext(id):
    session["showfulltext"] = not session["showfulltext"]
    return redirect(url_for("main.page", id=id))


@main.route("/tags/<tag>")
def tags(tag):
    for d in session["tags"]:
        if d["name"] == tag:
            if d["mark"] == False:
                d.update({"mark": True})
                session["condition"]["must"].append({"terms": {"auto_tags": [tag]}})
                session["from_hit"] = 0
                session["to_hit"] = 10
            else:
                d.update({"mark": False})
                session["condition"]["must"].remove({"terms": {"auto_tags": [tag]}})
                session["from_hit"] = 0
                session["to_hit"] = 10
            break
    return redirect(url_for("main.results"))


@main.route("/oldsearch/<search>")
def oldsearch(search):
    session["query"] = search
    session["condition"] = analyze_input(session["query"])
    session["from_hit"] = 0
    session["to_hit"] = 10
    session["tags"] = []
    return redirect(url_for("main.results"))


@main.route("/newgraph", methods=["GET", "POST"])
def newgraph():
    session.pop("graph", None)
    return redirect(url_for("graph"))


@main.route("/graphnode/<id>/<key>", methods=["GET", "POST"])
def graphnode(id, key):
    session["graph"] = {
        "mode": "neighbor",
        "marked": [f"{id}/{key}"],
        "searchfield": "",
        "searchdropdown": [],
        "categories": [],
    }
    return redirect(url_for("graph"))


@main.route("/help")
def help():
    return render_template("work.html")


@main.route("/contact")
def contact():
    return render_template("work.html")
