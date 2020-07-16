import base64
from elasticsearch_dsl.query import Ids, MultiMatch
from flask import (
    g,
    render_template,
    session,
    redirect,
    url_for,
    make_response,
    jsonify,
    abort,
    current_app
) 
from . import main
from .forms import NameForm, PageButton, SortForm
from ..db import analyze_input, execute_query, add_search, link


@main.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if not "user" in session:
        session["user"] = None
        session["next"] = None
    if form.validate_on_submit():
        session["query"] = form.name.data
        session["condition"] = analyze_input(session["query"])
        session["from_hit"] = 0
        session["to_hit"] = 10
        session["tags"] = []
        return redirect(url_for("main.results"))
    return render_template("index.html", form=form)


@main.route("/total", methods=["GET", "POST"])
def total():
    prepared_search = current_app.config["SEARCH"].query(MultiMatch(query=session["query"]))
    results = prepared_search.execute()
    return jsonify({"total": str(results.hits.total.value)})


@main.route("/page/<id>", methods=["GET", "POST"])
def page(id):
    form = NameForm()
    pdf = PageButton()
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
            abort(404)  # change error 500 to error 404
        hit = results.hits[0]
        if 'abstract' in hit:
            hit.abstract = link(hit.abstract)
        data = current_app.config["COLLECTION"][id]["pdf"]
        if data:
            pdfexists = True
        else:
            pdfexists = False
        return render_template(
            "page.html", form=form, hit=hit, pdfexists=pdfexists, pdf=pdf
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
    data = current_app.config["COLLECTION"][id]["pdf"]
    data = base64.b64decode(data)
    response = make_response(data)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={id}.pdf"
    return response


@main.route("/results", methods=["GET", "POST"])
def results():
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
    else:
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


@main.route("/tags/<tag>")
def tags(tag):
    # TODO: add tags to search
    for d in session["tags"]:
        if d["name"] == tag:
            if d["mark"] == False:
                d.update({"mark": True})
                session["condition"]["must"].append({'terms': {'auto_tags' : [tag]}})
                session["from_hit"] = 0
                session["to_hit"] = 10
            else:
                d.update({"mark": False})
                session["condition"]["must"].remove({'terms': {'auto_tags' : [tag]}})
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

