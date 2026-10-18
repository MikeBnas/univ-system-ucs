import hashlib
import os


def hash_password(password: str) -> str:
  """Genera un hash seguro con salt aleatorio usando PBKDF2-HMAC-SHA256."""
  salt = os.urandom(16)
  pwd_hash = hashlib.pbkdf2_hmac(
      'sha256', password.encode('utf-8'), salt, 100000
  )
  return salt.hex() + '$' + pwd_hash.hex()


def verificar_password(stored_password: str, provided_password: str) -> bool:
  """Verifica si una contraseña ingresada coincide con el hash almacenado."""
  try:
    if '$' not in stored_password:
      # Compatibilidad por si hay contraseñas antiguas en texto plano
      return stored_password == provided_password

    salt_hex, pwd_hex = stored_password.split('$')
    salt = bytes.fromhex(salt_hex)
    stored_hash = bytes.fromhex(pwd_hex)
    provided_hash = hashlib.pbkdf2_hmac(
        'sha256', provided_password.encode('utf-8'), salt, 100000
    )
    return provided_hash == stored_hash
  except Exception:
    return False