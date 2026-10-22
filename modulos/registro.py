"""
Módulo: REGISTRO
Alta de alumnos, profesores, materias, grupos e inscripciones.
"""
from .guardar_datos import db, Usuario, Alumno, Profesor, Materia, Grupo, Inscripcion
from . import correos


class ErrorRegistro(Exception):
    pass


def _crear_usuario(nombre, email, password, rol):
    email = email.strip().lower()
    if Usuario.query.filter_by(email=email).first():
        raise ErrorRegistro(f"Ya existe un usuario con el correo {email}")
    u = Usuario(nombre=nombre.strip(), email=email, rol=rol)
    u.set_password(password)
    db.session.add(u)
    return u


def registrar_alumno(nombre, email, password, matricula, grupo_id=None, notificar=True):
    if Alumno.query.filter_by(matricula=matricula).first():
        raise ErrorRegistro(f"La matrícula {matricula} ya está registrada")
    u = _crear_usuario(nombre, email, password, "alumno")
    a = Alumno(usuario=u, matricula=matricula.strip(), grupo_id=grupo_id or None)
    db.session.add(a)
    db.session.commit()
    if notificar:
        correos.enviar_correo(u.email, "Bienvenido al sistema escolar",
                              f"Hola {u.nombre}, tu matrícula es {a.matricula}. "
                              f"Ya puedes entrar con tu correo.")
    return a


def registrar_profesor(nombre, email, password, numero_empleado):
    if Profesor.query.filter_by(numero_empleado=numero_empleado).first():
        raise ErrorRegistro(f"El número de empleado {numero_empleado} ya existe")
    u = _crear_usuario(nombre, email, password, "profesor")
    p = Profesor(usuario=u, numero_empleado=numero_empleado.strip())
    db.session.add(p)
    db.session.commit()
    return p


def registrar_control(nombre, email, password):
    u = _crear_usuario(nombre, email, password, "control")
    db.session.commit()
    return u


def crear_grupo(nombre):
    if Grupo.query.filter_by(nombre=nombre).first():
        raise ErrorRegistro(f"El grupo {nombre} ya existe")
    g = Grupo(nombre=nombre.strip())
    db.session.add(g)
    db.session.commit()
    return g


def crear_materia(nombre, clave, profesor_id=None):
    if Materia.query.filter_by(clave=clave).first():
        raise ErrorRegistro(f"La clave {clave} ya existe")
    m = Materia(nombre=nombre.strip(), clave=clave.strip(), profesor_id=profesor_id or None)
    db.session.add(m)
    db.session.commit()
    return m


def inscribir(alumno_id, materia_id):
    if Inscripcion.query.filter_by(alumno_id=alumno_id, materia_id=materia_id).first():
        raise ErrorRegistro("El alumno ya está inscrito en esa materia")
    i = Inscripcion(alumno_id=alumno_id, materia_id=materia_id)
    db.session.add(i)
    db.session.commit()
    return i


def inscribir_grupo(grupo_id, materia_id):
    """Inscribe a todos los alumnos de un grupo en una materia. Regresa cuántos se inscribieron."""
    n = 0
    for a in Alumno.query.filter_by(grupo_id=grupo_id).all():
        if not Inscripcion.query.filter_by(alumno_id=a.id, materia_id=materia_id).first():
            db.session.add(Inscripcion(alumno_id=a.id, materia_id=materia_id))
            n += 1
    db.session.commit()
    return n
