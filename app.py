"""
Sistema de Control Escolar - punto de entrada (Coordinación de flujo).

Correr:  python app.py   ->  http://127.0.0.1:5000
"""
import os
from flask import Flask, redirect, url_for, session
from modulos.guardar_datos import db
from vistas.auth import auth_bp
from vistas.alumno import alumno_bp
from vistas.profesor import profesor_bp
from vistas.control import control_bp

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def cargar_env():
    """Lee un archivo .env sencillo (CLAVE=valor) sin dependencias extra."""
    ruta = os.path.join(BASE_DIR, ".env")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#") and "=" in linea:
                    k, v = linea.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def create_app():
    cargar_env()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cambia-esta-clave")
    # SQLite por defecto. Para MySQL de Laragon pon en .env:
    # DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/control_escolar
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "escuela.db"))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(alumno_bp, url_prefix="/alumno")
    app.register_blueprint(profesor_bp, url_prefix="/profesor")
    app.register_blueprint(control_bp, url_prefix="/control")

    @app.route("/")
    def inicio():
        rol = session.get("rol")
        if rol == "alumno":
            return redirect(url_for("alumno.inicio"))
        if rol == "profesor":
            return redirect(url_for("profesor.inicio"))
        if rol == "control":
            return redirect(url_for("control.inicio"))
        return redirect(url_for("auth.login"))

    @app.template_filter("dinero")
    def dinero(v):
        return f"${v:,.2f}"

    @app.template_filter("cal")
    def cal(v):
        return "—" if v is None or v == "" else f"{v:.1f}"

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
