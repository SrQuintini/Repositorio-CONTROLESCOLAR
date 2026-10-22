"""
Llena la base de datos con datos de prueba.
Uso:  python seed.py        (borra todo y vuelve a crear)
Todas las contraseñas son 1234.
"""
import random
from datetime import date, timedelta
from app import app
from modulos.guardar_datos import db
from modulos import registro, promedios, colegiaturas

with app.app_context():
    db.drop_all()
    db.create_all()
    random.seed(7)

    registro.registrar_control("Coordinación Escolar", "control@escuela.mx", "1234")

    g3a = registro.crear_grupo("3A")
    g3b = registro.crear_grupo("3B")

    garcia = registro.registrar_profesor("Laura García", "profe.garcia@escuela.mx", "1234", "P-001")
    lopez = registro.registrar_profesor("Miguel López", "profe.lopez@escuela.mx", "1234", "P-002")

    materias = [
        registro.crear_materia("Matemáticas", "MAT-301", garcia.id),
        registro.crear_materia("Programación", "PRG-301", garcia.id),
        registro.crear_materia("Bases de Datos", "BD-301", lopez.id),
        registro.crear_materia("Inglés", "ING-301", lopez.id),
    ]

    alumnos = [
        ("Ana Torres", "ana@escuela.mx", "A2026001", g3a),
        ("Juan Pérez", "juan@escuela.mx", "A2026002", g3a),
        ("Fernanda Ruiz", "fer@escuela.mx", "A2026003", g3a),
        ("Joaquín Méndez", "joaco@escuela.mx", "A2026004", g3b),
        ("Israel Ortega", "israel@escuela.mx", "A2026005", g3b),
        ("Tania Flores", "tania@escuela.mx", "A2026006", g3b),
    ]
    for nombre, email, mat, g in alumnos:
        registro.registrar_alumno(nombre, email, "1234", mat, g.id, notificar=False)

    for m in materias:
        registro.inscribir_grupo(g3a.id, m.id)
        registro.inscribir_grupo(g3b.id, m.id)

    # calificaciones de los parciales 1 y 2
    for m in materias:
        for i in m.inscripciones:
            base = random.uniform(5.0, 9.8)
            for p in (1, 2):
                promedios.guardar_calificacion(i.id, p, round(min(10, max(0, base + random.uniform(-1, 1))), 1))

    hoy = date.today()
    colegiaturas.generar_cargo_masivo("Colegiatura Septiembre 2026", 2500, hoy - timedelta(days=40))
    colegiaturas.generar_cargo_masivo("Colegiatura Octubre 2026", 2500, hoy - timedelta(days=5))
    colegiaturas.generar_cargo_masivo("Colegiatura Noviembre 2026", 2500, hoy + timedelta(days=15))

    # algunos pagos
    from modulos.guardar_datos import Colegiatura
    for c in Colegiatura.query.all():
        if "Septiembre" in c.concepto or ("Octubre" in c.concepto and c.alumno_id % 2):
            c.pagado = True
            c.fecha_pago = c.fecha_limite - timedelta(days=2)
    db.session.commit()

    print("Datos de prueba listos. Entra con control@escuela.mx / 1234")
