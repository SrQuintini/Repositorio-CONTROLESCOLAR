"""
Módulo: GUARDAR DATOS (servicio compartido)
Define la base de datos y todas las tablas. Los demás módulos leen/escriben aquí.
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # alumno | profesor | control
    activo = db.Column(db.Boolean, default=True)
    creado = db.Column(db.DateTime, default=datetime.utcnow)

    alumno = db.relationship("Alumno", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    profesor = db.relationship("Profesor", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Grupo(db.Model):
    __tablename__ = "grupos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # ej. "3A"
    alumnos = db.relationship("Alumno", back_populates="grupo")


class Alumno(db.Model):
    __tablename__ = "alumnos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    matricula = db.Column(db.String(30), unique=True, nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey("grupos.id"))
    usuario = db.relationship("Usuario", back_populates="alumno")
    grupo = db.relationship("Grupo", back_populates="alumnos")
    inscripciones = db.relationship("Inscripcion", back_populates="alumno", cascade="all, delete-orphan")
    colegiaturas = db.relationship("Colegiatura", back_populates="alumno", cascade="all, delete-orphan")


class Profesor(db.Model):
    __tablename__ = "profesores"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    numero_empleado = db.Column(db.String(30), unique=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="profesor")
    materias = db.relationship("Materia", back_populates="profesor")


class Materia(db.Model):
    __tablename__ = "materias"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    clave = db.Column(db.String(20), unique=True, nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesores.id"))
    profesor = db.relationship("Profesor", back_populates="materias")
    inscripciones = db.relationship("Inscripcion", back_populates="materia", cascade="all, delete-orphan")


class Inscripcion(db.Model):
    """Un alumno inscrito en una materia."""
    __tablename__ = "inscripciones"
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), nullable=False)
    alumno = db.relationship("Alumno", back_populates="inscripciones")
    materia = db.relationship("Materia", back_populates="inscripciones")
    calificaciones = db.relationship("Calificacion", back_populates="inscripcion", cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("alumno_id", "materia_id"),)


class Calificacion(db.Model):
    __tablename__ = "calificaciones"
    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey("inscripciones.id"), nullable=False)
    parcial = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    valor = db.Column(db.Float, nullable=False)      # 0 - 10
    inscripcion = db.relationship("Inscripcion", back_populates="calificaciones")
    __table_args__ = (db.UniqueConstraint("inscripcion_id", "parcial"),)


class Colegiatura(db.Model):
    __tablename__ = "colegiaturas"
    id = db.Column(db.Integer, primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    concepto = db.Column(db.String(80), nullable=False)  # ej. "Colegiatura Octubre 2026"
    monto = db.Column(db.Float, nullable=False)
    fecha_limite = db.Column(db.Date, nullable=False)
    pagado = db.Column(db.Boolean, default=False)
    fecha_pago = db.Column(db.Date)
    alumno = db.relationship("Alumno", back_populates="colegiaturas")

    @property
    def vencida(self):
        return not self.pagado and self.fecha_limite < date.today()


class CorreoEnviado(db.Model):
    """Bitácora de correos (los envíe o no el servidor SMTP)."""
    __tablename__ = "correos"
    id = db.Column(db.Integer, primary_key=True)
    destinatario = db.Column(db.String(120), nullable=False)
    asunto = db.Column(db.String(200), nullable=False)
    cuerpo = db.Column(db.Text, nullable=False)
    enviado = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
