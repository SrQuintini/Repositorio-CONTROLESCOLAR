# Sistema de Control Escolar (Python + Flask)

Tres vistas con login por rol y base de datos:

| Vista | Qué puede hacer |
|---|---|
| **Alumno** | Ver su boleta (parciales, promedio, estatus) y sus colegiaturas/adeudo |
| **Profesor** | Ver sus materias, capturar calificaciones por parcial, descargar CSV |
| **Control Escolar** | Registrar alumnos/profesores, crear materias y grupos, inscribir, cobrar colegiaturas, enviar recordatorios, reportes y bitácora de correos |

## Cómo correrlo (Windows / Laragon)

Abre la terminal de Laragon (o PowerShell) en la carpeta del proyecto:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py        # crea la BD con datos de prueba
python app.py
```

Abre http://127.0.0.1:5000 — todas las cuentas de prueba usan la contraseña `1234`:

- Control escolar: `control@escuela.mx`
- Profesor: `profe.garcia@escuela.mx`, `profe.lopez@escuela.mx`
- Alumno: `ana@escuela.mx`, `juan@escuela.mx`, `fer@escuela.mx`, …

## Base de datos

- **Por defecto: SQLite** (archivo `escuela.db`), no hay que instalar nada.
- **MySQL de Laragon:** arranca Laragon, crea la base `control_escolar` (botón *Database*), copia `.env.example` a `.env` y descomenta
  `DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/control_escolar`. Luego `python seed.py`.

Las tablas se crean solas al arrancar. `seed.py` **borra todo** y vuelve a cargar datos de prueba.

## Estructura (igual que el diagrama del pizarrón)

```
app.py                  Coordinación de flujo (arranca la app y registra las vistas)
modulos/
  guardar_datos.py      Guardar Datos  – modelos/tablas (servicio compartido)
  correos.py            Enviar Correos – SMTP + bitácora (servicio compartido)
  registro.py           Registro       – alta de alumnos, profesores, materias, grupos, inscripciones
  promedios.py          Promedios      – calificaciones y promedios
  colegiaturas.py       Colegiaturas   – cargos, pagos, recordatorios
  reportes.py           Reportes       – resumen y CSV
vistas/
  auth.py               Login y permisos por rol
  alumno.py / profesor.py / control.py
templates/              Pantallas HTML de cada vista
```

Cada equipo puede trabajar en su módulo sin pisar a los demás: los módulos solo se comunican a través de `guardar_datos.py` y `correos.py`.

## Tablas

`usuarios` (con rol), `alumnos`, `profesores`, `grupos`, `materias`, `inscripciones`, `calificaciones` (3 parciales, 0–10), `colegiaturas`, `correos`.

## Subirlo a GitHub

```bash
git init
git add .
git commit -m "Código base funcional"
git branch -M main
git remote add origin https://github.com/SrQuintini/Repositorio-CONTROLESCOLAR.git
git push -u origin main
```
