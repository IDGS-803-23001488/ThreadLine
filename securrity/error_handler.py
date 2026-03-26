# security/error_handler.py
from flask import render_template

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden(e):
    if request.path.startswith("/api"):
        return {"error": "Forbidden", "detalle": e.description}, 403
    return render_template("403.html", error=e.description), 403
