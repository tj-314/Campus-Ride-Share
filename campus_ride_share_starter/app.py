import os
import secrets
from pathlib import Path
from functools import wraps
from flask import Flask, request, session, redirect, url_for, render_template, flash, abort
from service import PostService
from models import ValidationError

def create_app(database=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    service = PostService(database or Path(__file__).with_name("rides.db"))
    app.extensions["posts"] = service

    @app.context_processor
    def context():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(24)
        return {"csrf": session["csrf"], "student": session.get("student")}

    @app.before_request
    def csrf_check():
        if request.method == "POST" and not secrets.compare_digest(request.form.get("csrf", ""), session.get("csrf", "missing")):
            abort(400)

    def protected(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if not session.get("student"):
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return wrapped

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            identity = request.form.get("identity")
            if identity not in ("demo-alex", "demo-jordan"):
                flash("Access denied: inactive or unknown demo account.")
            else:
                session.clear()
                session["student"] = identity
                return redirect(url_for("index"))
        return render_template("login.html")

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    @protected
    def index():
        rows = service.browse(session["student"], request.args.get("destination", ""), request.args.get("travel_date", ""), request.args.get("mine") == "1")
        return render_template("index.html", posts=rows)

    @app.get("/posts/<int:post_id>")
    @protected
    def detail(post_id):
        return render_template("detail.html", post=service.get(session["student"], post_id))

    @app.route("/create", methods=["GET", "POST"])
    @app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
    @protected
    def form(post_id=None):
        data, errors = {}, {}
        if post_id is not None:
            data = service.get(session["student"], post_id)
            service.authorize_owner(session["student"], data["owner"])
        if request.method == "POST":
            data = request.form.to_dict()
            try:
                if post_id is None:
                    service.create(session["student"], data)
                    flash("Post created successfully.")
                else:
                    service.update(session["student"], post_id, data)
                    flash("Post updated successfully.")
                return redirect(url_for("index"))
            except ValidationError as exc:
                errors = exc.errors
            except ValueError as exc:
                errors = {"post_type": str(exc)}
        return render_template("form.html", data=data, errors=errors, editing=post_id is not None)

    @app.route("/posts/<int:post_id>/delete", methods=["GET", "POST"])
    @protected
    def delete(post_id):
        post = service.get(session["student"], post_id)
        service.authorize_owner(session["student"], post["owner"])
        if request.method == "POST":
            removed = service.delete(session["student"], post_id, request.form.get("confirm") == "yes")
            flash("Post deleted successfully." if removed else "Deletion canceled; post unchanged.")
            return redirect(url_for("index"))
        return render_template("delete.html", post=post)

    @app.errorhandler(PermissionError)
    def forbidden(exc):
        return str(exc), 403

    @app.errorhandler(LookupError)
    def missing(exc):
        return str(exc), 404

    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
