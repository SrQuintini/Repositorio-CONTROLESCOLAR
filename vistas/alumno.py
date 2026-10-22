"""Vista ALUMNO: consulta boleta, promedio y colegiaturas (solo lectura)."""
from flask import Blueprint, render_template
from .auth import requiere_rol, usuario_actual
from modulos import promedios, colegiaturas

alumno_bp = Blueprint("alumno", __name__)


@alumno_bp.route("/")
@requiere_rol("alumno")
def inicio():
    alumno = usuario_actual().alumno
    return render_template(
        "alumno/inicio.html",
        alumno=alumno,
        boleta=promedios.boleta(alumno),
        promedio=promedios.promedio_general(alumno),
        cargos=sorted(alumno.colegiaturas, key=lambda c: c.fecha_limite),
        adeudo=colegiaturas.adeudo_total(alumno),
    )
