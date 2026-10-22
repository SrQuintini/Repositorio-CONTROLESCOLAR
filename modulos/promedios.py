"""
Módulo: PROMEDIOS
Captura de calificaciones y cálculo de promedios.
"""
from .guardar_datos import db, Calificacion, Inscripcion, Alumno

PARCIALES = (1, 2, 3)
CALIFICACION_MINIMA = 6.0


def guardar_calificacion(inscripcion_id, parcial, valor):
    valor = float(valor)
    if not 0 <= valor <= 10:
        raise ValueError("La calificación debe estar entre 0 y 10")
    if parcial not in PARCIALES:
        raise ValueError("Parcial inválido")
    c = Calificacion.query.filter_by(inscripcion_id=inscripcion_id, parcial=parcial).first()
    if c:
        c.valor = valor
    else:
        db.session.add(Calificacion(inscripcion_id=inscripcion_id, parcial=parcial, valor=valor))
    db.session.commit()


def calificaciones_por_parcial(inscripcion):
    """Regresa {1: 8.5, 2: None, 3: None}"""
    datos = {p: None for p in PARCIALES}
    for c in inscripcion.calificaciones:
        datos[c.parcial] = c.valor
    return datos


def promedio_materia(inscripcion):
    vals = [c.valor for c in inscripcion.calificaciones]
    return round(sum(vals) / len(vals), 2) if vals else None


def promedio_general(alumno):
    proms = [p for p in (promedio_materia(i) for i in alumno.inscripciones) if p is not None]
    return round(sum(proms) / len(proms), 2) if proms else None


def estatus(promedio):
    if promedio is None:
        return "Sin calificar"
    return "Aprobado" if promedio >= CALIFICACION_MINIMA else "Reprobado"


def boleta(alumno):
    """Lista de dicts con la info de cada materia del alumno."""
    filas = []
    for i in alumno.inscripciones:
        prom = promedio_materia(i)
        filas.append({
            "materia": i.materia.nombre,
            "clave": i.materia.clave,
            "profesor": i.materia.profesor.usuario.nombre if i.materia.profesor else "—",
            "parciales": calificaciones_por_parcial(i),
            "promedio": prom,
            "estatus": estatus(prom),
        })
    return filas
