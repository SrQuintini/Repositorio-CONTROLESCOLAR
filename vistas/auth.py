"""Login, logout y control de acceso por rol."""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modulos.guardar_datos import db, Usuario

auth_bp = Blueprint("auth", __name__)


def requiere_rol(*roles):
    def deco(f):
        @wraps(f)
        def envoltura(*args, **kwargs):
            if session.get("rol") not in roles:
                flash("Inicia sesión con una cuenta autorizada.", "error")
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return envoltura
    return deco


def usuario_actual():
    uid = session.get("usuario_id")
    return db.session.get(Usuario, uid) if uid else None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        u = Usuario.query.filter_by(email=email).first()
        if u and u.activo and u.check_password(request.form.get("password", "")):
            session.clear()
            session["usuario_id"] = u.id
            session["rol"] = u.rol
            session["nombre"] = u.nombre
            return redirect(url_for("inicio"))
        flash("Correo o contraseña incorrectos.", "error")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
