"""
Módulo: ENVIAR CORREOS (servicio compartido)
Si configuras SMTP en variables de entorno, manda correos reales.
Si no, solo los guarda en la bitácora (tabla `correos`) para que puedas verlos en Control Escolar.

Variables de entorno (opcionales):
  SMTP_HOST=smtp.gmail.com  SMTP_PORT=587  SMTP_USER=tu@correo.com  SMTP_PASS=contraseña_de_aplicacion
"""
import os
import smtplib
from email.message import EmailMessage
from .guardar_datos import db, CorreoEnviado


def enviar_correo(destinatario, asunto, cuerpo):
    enviado = False
    host = os.getenv("SMTP_HOST")
    if host:
        try:
            msg = EmailMessage()
            msg["From"] = os.getenv("SMTP_USER")
            msg["To"] = destinatario
            msg["Subject"] = asunto
            msg.set_content(cuerpo)
            with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", 587)), timeout=10) as s:
                s.starttls()
                s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
                s.send_message(msg)
            enviado = True
        except Exception as e:  # no tumbar la app si falla el correo
            print(f"[correos] No se pudo enviar a {destinatario}: {e}")

    db.session.add(CorreoEnviado(destinatario=destinatario, asunto=asunto, cuerpo=cuerpo, enviado=enviado))
    db.session.commit()
    return enviado
