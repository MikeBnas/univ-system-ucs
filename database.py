from pymongo import MongoClient
from modules.security import hash_password

try:
  client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
  db = client["gestion_academica"]
  client.server_info()
  db_conectada = True
except Exception:
  db_conectada = False


def get_db():
  return db

def inicializar_admin_por_defecto():
  db = get_db()
  usuarios_col = db['usuarios']
  admin_existente = usuarios_col.find_one({'usuario': 'Administrador'})

  if not admin_existente:
    usuarios_col.insert_one({
        'usuario': 'Administrador',
        'cedula': '00000000',
        'email': 'admin@ucs.edu.ve',
        'password': hash_password(
            'Limala2121#$'
        ),  # <--- Contraseña cifrada de fábrica
        'rol': 'Administrador',
    })