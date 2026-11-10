import streamlit as st
from database import get_db
from modules.security import hash_password, verificar_password

def render():
    st.subheader("🔑 Recuperación de Contraseña (Verificación Institucional)")
    st.info("Ingresa tu correo o usuario junto con tu número de cédula para validar tu identidad.")

    db = get_db()
    usuarios_col = db["usuarios"]

    if "paso_recup" not in st.session_state:
        st.session_state.paso_recup = 1
    if "user_id_recup" not in st.session_state:
        st.session_state.user_id_recup = None

    # PASO 1: Validar Identidad (Usuario/Correo + Cédula)
    if st.session_state.paso_recup == 1:
        with st.form("form_validar_identidad"):
            usuario_input = st.text_input("Usuario o Correo Registrado").strip()
            cedula_input = st.text_input("Cédula de Identidad (sin puntos)").strip()
            btn_validar = st.form_submit_button("🔍 Verificar Datos", type="primary")

        if btn_validar:
            if not usuario_input or not cedula_input:
                st.error("Por favor completa todos los campos.")
            else:
                # Limpiar cédula
                cedula_limpia = "".join(c for c in cedula_input if c.isdigit())
                
                # Buscar en la colección de usuarios
                user_doc = usuarios_col.find_one({
                    "$or": [{"usuario": usuario_input}, {"email": usuario_input}, {"correo": usuario_input}]
                })

                if user_doc:
                    cedula_guardada = str(user_doc.get("cedula", "")).strip()
                    if cedula_guardada == cedula_limpia and cedula_limpia != "":
                        st.session_state.user_id_recup = user_doc["_id"]
                        st.session_state.paso_recup = 2
                        st.success("¡Identidad verificada exitosamente!")
                        st.rerun()
                    else:
                        st.error("La cédula ingresada no coincide con los registros del usuario.")
                else:
                    st.error("No se encontró ningún usuario con los datos ingresados.")

    # PASO 2: Restablecer Contraseña
    elif st.session_state.paso_recup == 2:
        st.subheader("🔒 Ingresa tu Nueva Contraseña")

        with st.form("form_nueva_clave"):
            nueva_pass = st.text_input("Nueva Contraseña", type="password")
            confirmar_pass = st.text_input("Confirmar Nueva Contraseña", type="password")
            btn_guardar = st.form_submit_button("💾 Actualizar Contraseña", type="primary")

        if btn_guardar:
            if not nueva_pass or not confirmar_pass:
                st.error("Ingresa y confirma la nueva contraseña.")
            elif nueva_pass != confirmar_pass:
                st.error("Las contraseñas no coinciden.")
            elif len(nueva_pass) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            else:
                # Actualizar contraseña cifrada con hash
                usuarios_col.update_one(
                    {"_id": st.session_state.user_id_recup},
                    {"$set": {"password": hash_password(nueva_pass)}}
                )
                st.success("¡Contraseña actualizada con éxito! Ya puedes iniciar sesión con tu nueva clave.")
                st.session_state.paso_recup = 1
                st.session_state.user_id_recup = None

        if st.button("⬅️ Cancelar"):
            st.session_state.paso_recup = 1
            st.session_state.user_id_recup = None
            st.rerun()
