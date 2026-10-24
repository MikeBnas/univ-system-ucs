import random
import string
from datetime import datetime, timedelta
import resend
import streamlit as st
from database import get_db
from modules.security import hash_password


def generar_codigo_aleatorio(length=6):
  """Genera un código alfanumérico seguro de 6 dígitos para la recuperación"""
  return "".join(
      random.choices(string.ascii_uppercase + string.digits, k=length)
  )


def render():
  st.subheader("🔑 Recuperación de Contraseña")
  st.info(
      "Ingresa tu correo electrónico registrado para enviarte un código temporal"
      " de recuperación."
  )

  db = get_db()
  usuarios_col = db["usuarios"]

  # Obtener la API key de Resend desde los secretos de Streamlit
  try:
    resend.api_key = st.secrets["general"]["RESEND_API_KEY"]
  except Exception:
    st.error(
        "⚠️ La API Key de Resend no está configurada en los secretos de"
        " Streamlit."
    )
    return

  with st.form("form_recuperar"):
    correo_ingresado = st.text_input(
        "Correo Electrónico Registrado"
    ).strip().lower()
    btn_enviar = st.form_submit_button("📤 Enviar Código de Recuperación")

  if btn_enviar:
    if not correo_ingresado:
      st.error("Por favor, introduce un correo electrónico.")
    else:
      # Buscar usuario por correo o email en MongoDB de forma flexible
      usuario = usuarios_col.find_one({
          "$or": [{"correo": correo_ingresado}, {"email": correo_ingresado}]
      })

      if usuario:
        # Generar token de 6 caracteres y fecha de expiración (15 minutos)
        token = generar_codigo_aleatorio()
        expiracion = datetime.utcnow() + timedelta(minutes=15)

        # Identificar qué campo de correo usa el documento encontrado
        filtro_correo = usuario.get("email", usuario.get("email", correo_ingresado))

        # Guardar el token temporal y su expiración en el documento del usuario
        usuarios_col.update_one(
            {"$or": [{"correo": filtro_correo}, {"email": filtro_correo}]},
            {
                "$set": {
                    "reset_token": token,
                    "reset_expiracion": expiracion,
                }
            },
        )

        # Estructurar el correo electrónico usando Resend
        params = {
            "from": "Sistema Académico <onboarding@resend.dev>",
            "to": [correo_ingresado],
            "subject": "Código de Recuperación de Contraseña",
            "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                    <h2 style="color: #2b6cb0;">Recuperación de Contraseña</h2>
                    <p>Has solicitado restablecer tu contraseña en el sistema académico.</p>
                    <p>Tu código de recuperación temporal es:</p>
                    <div style="background: #edf2f7; padding: 10px 20px; font-size: 24px; font-weight: bold; letter-spacing: 2px; display: inline-block; border-radius: 5px; color: #2d3748;">
                        {token}
                    </div>
                    <p style="margin-top: 20px; font-size: 12px; color: #718096;">Este código expira en 15 minutos. Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
                </div>
            """,
        }

        try:
          response = resend.Emails.send(params)
          st.success(
              "¡Correo enviado con éxito! Revisa tu bandeja de entrada o spam."
          )
          st.session_state["paso_recuperacion"] = "verificar"
          st.session_state["correo_recuperando"] = correo_ingresado
        except Exception as e:
          st.error(f"Error al enviar el correo a través de Resend: {e}")
      else:
        st.warning(
            "No se encontró ningún usuario registrado con ese correo electrónico."
        )

  # Si el correo ya fue enviado, mostramos el formulario para introducir el código y la nueva contraseña
  if st.session_state.get("paso_recuperacion") == "verificar":
    st.markdown("---")
    st.subheader("🔒 Restablecer Contraseña")

    with st.form("form_reset_password"):
      codigo_ingresado = st.text_input(
          "Introduce el código de 6 dígitos recibido"
      ).strip().upper()
      nueva_pass = st.text_input(
          "Nueva Contraseña", type="password"
      )
      confirmar_pass = st.text_input(
          "Confirmar Nueva Contraseña", type="password"
      )
      btn_cambiar = st.form_submit_button("💾 Guardar Nueva Contraseña")

    if btn_cambiar:
      correo_obj = st.session_state.get("correo_recuperando")
      user_data = usuarios_col.find_one({
          "$or": [{"correo": correo_obj}, {"email": correo_obj}]
      })

      if not user_data:
        st.error("Sesión de recuperación inválida. Vuelve a intentarlo.")
        return

      # Validar token y expiración
      token_valido = user_data.get("reset_token") == codigo_ingresado
      expiracion_valida = datetime.utcnow() <= user_data.get(
          "reset_expiracion", datetime.utcnow()
      )

      if not token_valido:
        st.error("El código de recuperación es incorrecto.")
      elif not expiracion_valida:
        st.error(
            "El código ha expirado. Solicita uno nuevo."
        )
      elif nueva_pass != confirmar_pass:
        st.error("Las contraseñas nuevas no coinciden.")
      elif len(nueva_pass) < 6:
        st.error("La contraseña debe tener al menos 6 caracteres.")
      else:
        # Actualizar contraseña cifrada con hash en MongoDB y limpiar tokens
        filtro_update = user_data.get("correo", user_data.get("email", correo_obj))
        
        usuarios_col.update_one(
            {"$or": [{"correo": filtro_update}, {"email": filtro_update}]},
            {
                "$set": {"password": hash_password(nueva_pass)},
                "$unset": {"reset_token": "", "reset_expiracion": ""},
            },
        )
        st.success(
            "¡Contraseña actualizada con éxito! Ya puedes iniciar sesión con tu"
            " nueva clave."
        )
        st.session_state["paso_recuperacion"] = None
        st.session_state["correo_recuperando"] = None
