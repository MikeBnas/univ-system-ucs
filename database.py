import streamlit as st
from pymongo import MongoClient
from modules.security import hash_password

@st.cache_resource
def init_connection():
  """Inicializa la conexión leyendo de forma segura los secretos de Streamlit."""
  try:
    # Intenta leer la URI exclusivamente desde los secretos
    if "mongo" in st.secrets and "uri" in st.secrets["mongo"]:
      mongo_uri = st.secrets["mongo"]["uri"]
    elif "general" in st.secrets and "MONGO_URI" in st.secrets["general"]:
      mongo_uri = st.secrets["general"]["MONGO_URI"]
    else:
      # Si no hay secretos configurados localmente, cae a un entorno local seguro por defecto
      mongo_uri = "mongodb://localhost:27017/"

    client = MongoClient(
        mongo_uri, 
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    
    client.server_info()
    return client
  except Exception as e:
    print(f"Error crítico de conexión a MongoDB: {e}")
    return None

client = init_connection()

if client is not None:
  db = client.get_default_database()
  if db is None:
    db = client["gestion_academica"]
  db_conectada = True
else:
  db = None
  db_conectada = False


def get_db():
  return db


def inicializar_admin_por_defecto():
  if not db_conectada or db is None:
    return
    
  usuarios_col = db['usuarios']
  
  admin_existente = usuarios_col.find_one({
      '$or': [
          {'usuario': 'Administrador'},
          {'usuario': 'admin'},
          {'rol': 'Administrador'}
      ]
  })

  if not admin_existente:
    usuarios_col.insert_one({
        'usuario': 'Administrador',
        'cedula': '00000000',
        'email': 'admin@ucs.edu.ve',
        'password': hash_password('Limala2121#$'),
        'rol': 'Administrador',
    })
