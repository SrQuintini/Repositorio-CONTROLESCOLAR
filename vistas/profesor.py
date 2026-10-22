"""Vista PROFESOR: ve sus materias y captura calificaciones."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response
from .auth import requiere_rol, usuario_actual
from modulos.guardar_datos import db, Materia
from modulos import promedios, reportes

profesor_bp = Blueprint("profesor", __name__)


def _materia_propia(materia_id):
    m = db.session.get(Materia, materia_id)
    if m is None or m.profesor_id != usuario_actual().profesor.id:
        abort(404)
    return m


@profesor_bp.route("/")
@requiere_rol("profesor")
def inicio():
    prof = usuario_actual().profesor
    resumen = []
    for m in prof.materias:
        filas = reportes.reporte_materia(m)
        proms = [f["promedio"] for f in filas if f["promedio"] is not None]
        resumen.append({
            "materia": m,
            "alumnos": len(filas),
            "promedio": round(sum(proms) / len(proms), 2) if proms else None,
            "reprobados": sum(1 for f in filas if f["estatus"] == "Reprobado"),
        })
    return render_template("profesor/inicio.html", resumen=resumen)


@profesor_bp.route("/materia/<int:materia_id>", methods=["GET", "POST"])
@requiere_rol("profesor")
def materia(materia_id):
    m = _materia_propia(materia_id)
    if request.method == "POST":
        errores = 0
        for i in m.inscripciones:
            for p in promedios.PARCIALES:
                valor = request.form.get(f"cal_{i.id}_{p}", "").strip()
                if valor == "":
                    continue
                try:
                    promedios.guardar_calificacion(i.id, p, valor)
                except ValueError:
                    errores += 1
        if errores:
            flash(f"{errores} calificación(es) inválidas no se guardaron (deben ser de 0 a 10).", "error")
        else:
            flash("Calificaciones guardadas.", "ok")
        return redirect(url_for("profesor.materia", materia_id=m.id))

    inscripciones = sorted(m.inscripciones, key=lambda i: i.alumno.usuario.nombre)
    filas = [{"insc": i, "parciales": promedios.calificaciones_por_parcial(i),
              "promedio": promedios.promedio_materia(i)} for i in inscripciones]
    return render_template("profesor/materia.html", materia=m, filas=filas,
                           parciales=promedios.PARCIALES, estatus=promedios.estatus)


@profesor_bp.route("/materia/<int:materia_id>/csv")
@requiere_rol("profesor")
def materia_csv(materia_id):
    m = _materia_propia(materia_id)
    filas = []
    for f in reportes.reporte_materia(m):
        p = f.pop("parciales")
        filas.append({**{k: f[k] for k in ("matricula", "nombre")},
                      "P1": p[1] or "", "P2": p[2] or "", "P3": p[3] or "",
                      "promedio": f["promedio"] or "", "estatus": f["estatus"]})
    return Response(reportes.a_csv(filas), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={m.clave}.csv"})
