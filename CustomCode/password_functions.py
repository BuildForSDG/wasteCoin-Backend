import bcrypt
import re

def generate_password_hash(user_password):
    encoded_password = user_password.encode('utf-8')
    hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
    app_regex = re.compile("b*'")
    encoding_removed = app_regex.sub("",str(hashed_password))
    return encoding_removed

def check_password_match(user_password, hashed_password):
    encoded_password = user_password.encode('utf-8')
    encoded_hashed_password = hashed_password.encode('utf-8')
    if bcrypt.checkpw(encoded_password, encoded_hashed_password):
        return True
    else:
        return False