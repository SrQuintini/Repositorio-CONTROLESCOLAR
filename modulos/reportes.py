"""
Módulo: REPORTES
Estadísticas generales y exportación a CSV.
"""
import csv
import io
from .guardar_datos import Alumno, Profesor, Materia, Colegiatura
from . import promedios, colegiaturas


def resumen_general():
    alumnos = Alumno.query.all()
    proms = [p for p in (promedios.promedio_general(a) for a in alumnos) if p is not None]
    cargos = Colegiatura.query.all()
    return {
        "total_alumnos": len(alumnos),
        "total_profesores": Profesor.query.count(),
        "total_materias": Materia.query.count(),
        "promedio_escuela": round(sum(proms) / len(proms), 2) if proms else None,
        "reprobados": sum(1 for p in proms if p < promedios.CALIFICACION_MINIMA),
        "cobrado": sum(c.monto for c in cargos if c.pagado),
        "por_cobrar": sum(c.monto for c in cargos if not c.pagado),
        "vencidos": sum(1 for c in cargos if c.vencida),
    }


def reporte_alumnos():
    filas = []
    for a in Alumno.query.order_by(Alumno.matricula).all():
        prom = promedios.promedio_general(a)
        filas.append({
            "matricula": a.matricula,
            "nombre": a.usuario.nombre,
            "email": a.usuario.email,
            "grupo": a.grupo.nombre if a.grupo else "",
            "promedio": prom if prom is not None else "",
            "estatus": promedios.estatus(prom),
            "adeudo": colegiaturas.adeudo_total(a),
        })
    return filas


def reporte_materia(materia):
    filas = []
    for i in materia.inscripciones:
        prom = promedios.promedio_materia(i)
        filas.append({
            "matricula": i.alumno.matricula,
            "nombre": i.alumno.usuario.nombre,
            "parciales": promedios.calificaciones_por_parcial(i),
            "promedio": prom,
            "estatus": promedios.estatus(prom),
        })
    return filas


def a_csv(filas):
    if not filas:
        return ""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(filas[0].keys()))
    w.writeheader()
    w.writerows(filas)
    return "﻿" + buf.getvalue()  # BOM para que Excel respete acentos
