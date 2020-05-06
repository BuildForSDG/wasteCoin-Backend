import random
import string


def alphanumeric(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.sample(lettersAndDigits, stringLength))

def alpha(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.sample(letters, stringLength))

def numeric(stringLength=8):
    Digits = string.digits
    return ''.join(random.sample(Digits, stringLength))



