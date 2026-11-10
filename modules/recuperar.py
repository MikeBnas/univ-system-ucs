import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def enviar_correo_smtp(destinatario, codigo):
    """
    Envía el correo de recuperación intentando múltiples puertos SMTP 
    para evadir bloqueos de ISP y evitar el error SMTP time out.
    """
    try:
        # Extraer credenciales desde los secretos de Streamlit
        if "gmail" in st.secrets:
            remitente = st.secrets["gmail"]["EMAIL"]
            password_app = st.secrets["gmail"]["APP_PASSWORD"]
        elif "GMAIL_EMAIL" in st.secrets:
            remitente = st.secrets["GMAIL_EMAIL"]
            password_app = st.secrets["GMAIL_APP_PASSWORD"]
        else:
            remitente = st.secrets["general"]["GMAIL_EMAIL"]
            password_app = st.secrets["general"]["GMAIL_APP_PASSWORD"]
    except KeyError:
        return False, "⚠️ Las credenciales de Gmail (EMAIL / APP_PASSWORD) no están configuradas en st.secrets."

    # Armar la estructura del mensaje MIME
    msg = MIMEMultipart()
    msg["From"] = f"Sistema Académico <{remitente}>"
    msg["To"] = destinatario
    msg["Subject"] = "Código de Recuperación de Contraseña"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2 style="color: #2b6cb0;">Recuperación de Contraseña</h2>
        <p>Has solicitado restablecer tu contraseña en el sistema académico.</p>
        <p>Tu código de recuperación temporal es:</p>
        <div style="background: #edf2f7; padding: 10px 20px; font-size: 24px; font-weight: bold; letter-spacing: 2px; display: inline-block; border-radius: 5px; color: #2d3748;">
            {codigo}
        </div>
        <p style="margin-top: 20px; font-size: 12px; color: #718096;">Este código expira en 15 minutos. Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
    </div>
    """
    msg.attach(MIMEText(html_content, "html"))

    # Lista de combinaciones de puertos y métodos de conexión para evadir bloqueos de red
    configuraciones_smtp = [
        {"puerto": 587, "tipo": "STARTTLS"},
        {"puerto": 2525, "tipo": "STARTTLS"},  # Puerto alternativo para ISPs restrictivos
        {"puerto": 465, "tipo": "SSL"}
    ]

    ultimo_error = ""

    for config in configuraciones_smtp:
        puerto = config["puerto"]
        tipo = config["tipo"]
        try:
            if tipo == "STARTTLS":
                # Timeout reducido a 5 segundos por intento para responder rápido
                with smtplib.SMTP("smtp.gmail.com", puerto, timeout=5) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(remitente, password_app)
                    server.send_message(msg)
                    return True, "¡Correo enviado con éxito! Revisa tu bandeja de entrada o spam."
            elif tipo == "SSL":
                with smtplib.SMTP_SSL("smtp.gmail.com", puerto, timeout=5) as server:
                    server.login(remitente, password_app)
                    server.send_message(msg)
                    return True, "¡Correo enviado con éxito! Revisa tu bandeja de entrada o spam."
        except Exception as err:
            ultimo_error = str(err)
            # Continúa al siguiente puerto si este falló o dio timeout
            continue

    return False, f"Error al enviar correo por SMTP (Todos los puertos fallaron por timeout): {ultimo_error}"
