from bcrypt import hashpw, gensalt, checkpw

def hash_password(password):
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    return hashed_password.decode('utf-8')

def verify_password(stored_password, provided_password):
    try:
        return checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    except ValueError: 
        return False