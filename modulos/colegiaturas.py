"""
Módulo: COLEGIATURAS
Cargos, pagos y adeudos.
"""
from datetime import date
from .guardar_datos import db, Colegiatura, Alumno
from . import correos


def generar_cargo(alumno_id, concepto, monto, fecha_limite):
    c = Colegiatura(alumno_id=alumno_id, concepto=concepto, monto=float(monto), fecha_limite=fecha_limite)
    db.session.add(c)
    db.session.commit()
    return c


def generar_cargo_masivo(concepto, monto, fecha_limite, grupo_id=None):
    """Genera el mismo cargo a todos los alumnos (o a un grupo)."""
    q = Alumno.query
    if grupo_id:
        q = q.filter_by(grupo_id=grupo_id)
    n = 0
    for a in q.all():
        db.session.add(Colegiatura(alumno_id=a.id, concepto=concepto, monto=float(monto), fecha_limite=fecha_limite))
        n += 1
    db.session.commit()
    return n


def registrar_pago(colegiatura_id):
    c = db.session.get(Colegiatura, colegiatura_id)
    if c is None:
        raise ValueError("Cargo no encontrado")
    c.pagado = True
    c.fecha_pago = date.today()
    db.session.commit()
    correos.enviar_correo(c.alumno.usuario.email, f"Pago recibido: {c.concepto}",
                          f"Hola {c.alumno.usuario.nombre}, registramos tu pago de "
                          f"${c.monto:,.2f} por {c.concepto}. ¡Gracias!")
    return c


def adeudo_total(alumno):
    return sum(c.monto for c in alumno.colegiaturas if not c.pagado)


def recordar_vencidas():
    """Envía recordatorio a cada alumno con cargos vencidos. Regresa cuántos correos se mandaron."""
    n = 0
    for a in Alumno.query.all():
        vencidas = [c for c in a.colegiaturas if c.vencida]
        if vencidas:
            lista = "\n".join(f"- {c.concepto}: ${c.monto:,.2f} (vencía {c.fecha_limite})" for c in vencidas)
            correos.enviar_correo(a.usuario.email, "Recordatorio de pagos vencidos",
                                  f"Hola {a.usuario.nombre}, tienes pagos pendientes:\n{lista}")
            n += 1
    return n
