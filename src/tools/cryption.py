from cryptography.fernet import Fernet
from json import loads, dumps

def decrypt(encrypted_data, key):
    cipher = Fernet(key)
    return loads(cipher.decrypt(encrypted_data).decode())

def encrypt(data, key):
    cipher = Fernet(key)
    return cipher.encrypt(dumps(data).encode())