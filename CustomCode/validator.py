import re


#Email Validator
re_email = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
def checkmail(email):
    if(re.search(re_email,email)):
        return True
    else:
        return False