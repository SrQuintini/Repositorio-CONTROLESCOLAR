"""Vista CONTROL ESCOLAR (admin): registro, materias, colegiaturas, reportes y correos."""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from .auth import requiere_rol
from modulos.guardar_datos import db, Alumno, Profesor, Materia, Grupo, Colegiatura, CorreoEnviado, Usuario
from modulos import registro, colegiaturas, reportes, promedios

control_bp = Blueprint("control", __name__)


def _ejecutar(fn, mensaje_ok):
    """Ejecuta una acción y muestra el resultado como mensaje."""
    try:
        fn()
        flash(mensaje_ok, "ok")
    except (registro.ErrorRegistro, ValueError) as e:
        db.session.rollback()
        flash(str(e), "error")


@control_bp.route("/")
@requiere_rol("control")
def inicio():
    return render_template("control/inicio.html", r=reportes.resumen_general())


# ---------- ALUMNOS ----------
@control_bp.route("/alumnos", methods=["GET", "POST"])
@requiere_rol("control")
def alumnos():
    if request.method == "POST":
        f = request.form
        _ejecutar(lambda: registro.registrar_alumno(
            f["nombre"], f["email"], f["password"], f["matricula"], f.get("grupo_id", type=int)),
            "Alumno registrado.")
        return redirect(url_for("control.alumnos"))
    return render_template("control/alumnos.html", filas=reportes.reporte_alumnos(),
                           grupos=Grupo.query.order_by(Grupo.nombre).all())


@control_bp.route("/alumnos/<matricula>")
@requiere_rol("control")
def alumno_detalle(matricula):
    a = Alumno.query.filter_by(matricula=matricula).first_or_404()
    return render_template("control/alumno_detalle.html", alumno=a, boleta=promedios.boleta(a),
                           promedio=promedios.promedio_general(a),
                           cargos=sorted(a.colegiaturas, key=lambda c: c.fecha_limite),
                           adeudo=colegiaturas.adeudo_total(a),
                           materias=Materia.query.order_by(Materia.nombre).all())


@control_bp.route("/alumnos/<int:alumno_id>/inscribir", methods=["POST"])
@requiere_rol("control")
def inscribir(alumno_id):
    a = db.get_or_404(Alumno, alumno_id)
    _ejecutar(lambda: registro.inscribir(a.id, request.form.get("materia_id", type=int)), "Alumno inscrito.")
    return redirect(url_for("control.alumno_detalle", matricula=a.matricula))


@control_bp.route("/usuarios/<int:usuario_id>/estado", methods=["POST"])
@requiere_rol("control")
def cambiar_estado(usuario_id):
    u = db.get_or_404(Usuario, usuario_id)
    u.activo = not u.activo
    db.session.commit()
    flash(f"{u.nombre} {'activado' if u.activo else 'desactivado'}.", "ok")
    return redirect(request.referrer or url_for("control.inicio"))


# ---------- PROFESORES ----------
@control_bp.route("/profesores", methods=["GET", "POST"])
@requiere_rol("control")
def profesores():
    if request.method == "POST":
        f = request.form
        _ejecutar(lambda: registro.registrar_profesor(f["nombre"], f["email"], f["password"], f["numero_empleado"]),
                  "Profesor registrado.")
        return redirect(url_for("control.profesores"))
    return render_template("control/profesores.html",
                           profesores=Profesor.query.order_by(Profesor.numero_empleado).all())


# ---------- MATERIAS Y GRUPOS ----------
@control_bp.route("/materias", methods=["GET", "POST"])
@requiere_rol("control")
def materias():
    if request.method == "POST":
        f = request.form
        accion = f.get("accion")
        if accion == "materia":
            _ejecutar(lambda: registro.crear_materia(f["nombre"], f["clave"], f.get("profesor_id", type=int)),
                      "Materia creada.")
        elif accion == "grupo":
            _ejecutar(lambda: registro.crear_grupo(f["nombre"]), "Grupo creado.")
        elif accion == "inscribir_grupo":
            n = registro.inscribir_grupo(f.get("grupo_id", type=int), f.get("materia_id", type=int))
            flash(f"{n} alumno(s) inscritos.", "ok")
        elif accion == "asignar":
            m = db.get_or_404(Materia, f.get("materia_id", type=int))
            m.profesor_id = f.get("profesor_id", type=int) or None
            db.session.commit()
            flash("Profesor asignado.", "ok")
        return redirect(url_for("control.materias"))
    return render_template("control/materias.html",
                           materias=Materia.query.order_by(Materia.clave).all(),
                           grupos=Grupo.query.order_by(Grupo.nombre).all(),
                           profesores=Profesor.query.all())


# ---------- COLEGIATURAS ----------
@control_bp.route("/colegiaturas", methods=["GET", "POST"])
@requiere_rol("control")
def colegiaturas_vista():
    if request.method == "POST":
        f = request.form
        accion = f.get("accion")
        if accion == "cargo":
            try:
                fecha = date.fromisoformat(f["fecha_limite"])
                n = colegiaturas.generar_cargo_masivo(f["concepto"], f["monto"], fecha, f.get("grupo_id", type=int))
                flash(f"Cargo generado a {n} alumno(s).", "ok")
            except ValueError:
                flash("Revisa el monto y la fecha.", "error")
        elif accion == "pagar":
            _ejecutar(lambda: colegiaturas.registrar_pago(f.get("colegiatura_id", type=int)), "Pago registrado.")
        elif accion == "recordatorios":
            n = colegiaturas.recordar_vencidas()
            flash(f"Se enviaron {n} recordatorio(s).", "ok")
        return redirect(request.referrer or url_for("control.colegiaturas_vista"))

    filtro = request.args.get("filtro", "pendientes")
    q = Colegiatura.query.join(Alumno)
    if filtro == "pendientes":
        q = q.filter(Colegiatura.pagado.is_(False))
    elif filtro == "pagados":
        q = q.filter(Colegiatura.pagado.is_(True))
    return render_template("control/colegiaturas.html", cargos=q.order_by(Colegiatura.fecha_limite).all(),
                           filtro=filtro, grupos=Grupo.query.order_by(Grupo.nombre).all())


# ---------- REPORTES Y CORREOS ----------
@control_bp.route("/reportes/alumnos.csv")
@requiere_rol("control")
def reporte_csv():
    return Response(reportes.a_csv(reportes.reporte_alumnos()), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=alumnos.csv"})


@control_bp.route("/correos")
@requiere_rol("control")
def correos():
    return render_template("control/correos.html",
                           correos=CorreoEnviado.query.order_by(CorreoEnviado.fecha.desc()).limit(100).all())
