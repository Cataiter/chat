import streamlit as st
import json
from datetime import datetime
import time # Para simular recarga periódica
import firebase_admin
from firebase_admin import credentials, firestore
from io import StringIO


# --- CONFIGURACIÓN DEL BACKEND (EL ARCHIVO COMPARTIDO) ---
st.set_page_config(page_title="Sala de Chat para Amigos")


# --- Inicializar Firebase ---
firebase_cfg = dict(st.secrets["firebase"])
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_cfg)
    firebase_admin.initialize_app(cred)

db = firestore.client()
messages_ref = db.collection("chat_messages")

# --- FUNCIONES DE BASE DE DATOS (LECTURA/ESCRITURA) ---
query = messages_ref.order_by("time")
results = query.stream()
def load_messages():
    query = messages_ref.order_by("time")
    return query.stream()


def save_message(user, content):
    """Guarda un nuevo mensaje en el archivo firebase."""
    
    new_message = {
        "user": user,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    messages_ref.add.append(new_message)
    

# --- INTERFAZ DE STREAMLIT ---

st.title("🗣️ Sala de Chat para Amigos (Demo)")
st.caption("Los mensajes se sincronizan a través del archivo `messages.json`.")

# Campo para que el usuario ingrese su nombre (se mantiene en la sesión)
if 'username' not in st.session_state:
    st.session_state['username'] = ''

st.sidebar.title("Tu Identidad")
user_input = st.sidebar.text_input("Ingresa tu nombre:", st.session_state['username'])
if user_input:
    st.session_state['username'] = user_input
    st.sidebar.success(f"Estás chateando como **{st.session_state['username']}**")
else:
    st.sidebar.warning("Por favor, ingresa tu nombre para empezar a chatear.")


# --- Mostrar el Historial de Mensajes ---

# Cargar los mensajes del archivo compartido (el 'backend')
chat_history = load_messages()

# Mostrar los mensajes en orden
for message in chat_history:
    message.to_dict()
    # Usamos el formato nativo de chat de Streamlit
    role = "user" if message["user"] == st.session_state['username'] else "assistant"
    
    with st.chat_message(role):
        st.write(f"**{message['user']}**")
        st.write(message["content"])

# --- Formulario de Entrada ---

if st.session_state['username']:
    # Usamos un contenedor para que el campo de entrada esté siempre abajo
    with st.container():
        st.markdown("---")
        
        # El formulario asegura que la entrada se borra al enviar
        with st.form("chat_form", clear_on_submit=True):
            prompt = st.text_input("Escribe tu mensaje aquí...", key="chat_input_key")
            submit_button = st.form_submit_button("Enviar Mensaje")

            if submit_button and prompt:
                # 1. Guardar el mensaje en el "backend" (el archivo JSON)
                save_message(st.session_state['username'], prompt)
                
                # 2. Forzar una recarga para que todos vean el nuevo mensaje
                st.rerun()
else:
    st.info("Por favor, ingresa tu nombre en la barra lateral para enviar mensajes.")


# --- Sincronización (Opcional) ---

# Usa un "empty" y un loop para recargar periódicamente los mensajes
# Esto simula un chat más "real time" sin que el usuario tenga que recargar el navegador.
# Si quieres desactivar la recarga automática, simplemente elimina las siguientes líneas.
st.text("Última actualización: " + datetime.now().strftime("%H:%M:%S"))
time.sleep(1) 

st.rerun()

