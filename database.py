import streamlit as st
from pymongo import MongoClient
from modules.security import hash_password

@st.cache_resource
def init_connection():
  """Inicializa la conexión leyendo de forma segura los secretos de Streamlit con fallback local."""
  mongo_uri = "mongodb://localhost:27017/"
  
  try:
    if "mongo" in st.secrets and "uri" in st.secrets["mongo"]:
      mongo_uri = st.secrets["mongo"]["uri"]
    elif "general" in st.secrets and "MONGO_URI" in st.secrets["general"]:
      mongo_uri = st.secrets["general"]["MONGO_URI"]
  except Exception:
    pass

  try:
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
  # Intentamos obtener la base de datos por defecto, si no existe en la URI, forzamos 'gestion_academica'
  try:
    db = client.get_default_database()
    if db is None or db.name == "test": # A veces por defecto toma 'test' si no se especifica
      db = client["gestion_academica"]
  except Exception:
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
