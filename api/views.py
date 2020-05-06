from datetime import datetime,timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import User,otp
from CustomCode import string_generator,password_functions,validator,autentication

# Create your views here.
@api_view(['GET'])
def index_page(request):
    return_data = {
        "error" : "0",
        "message" : "Successful",
    }
    return Response(return_data)

#User registration endpoint
@api_view(["POST"])
def user_registration(request):
    try:
        firstName = request.data.get('firstname',None)
        lastName = request.data.get('lastname',None)
        phoneNumber = request.data.get('phonenumber',None)
        email = request.data.get('email',None)
        gender = request.data.get('gender',None)
        password = request.data.get('password',None)
        address = request.data.get('address',None)
        lga = request.data.get('lga',None)
        state = request.data.get('state',None)
        country = request.data.get('country',None)
        reg_field = [firstName,lastName,phoneNumber,email,password,address,lga,state,country]
        if not None in reg_field and not "" in reg_field:
            if User.objects.filter(user_phone =phoneNumber).exists() or User.objects.filter(email =email).exists():
                return_data = {
                    "error": "1",
                    "message": "User Exists"
                }
            else:
                #generate user_id
                userRandomId = string_generator.alphanumeric(20)
                #encrypt password
                encryped_password = password_functions.generate_password_hash(password)
                #Save user_data
                new_userData = User(user_id=userRandomId,firstname=firstName,lastname=lastName,
                                email=email,user_phone=phoneNumber,user_gender=gender,
                                user_password=encryped_password,user_address=address,
                                user_state=state,user_LGA=lga,user_country=country)
                new_userData.save()
                #Generate OTP
                code = string_generator.numeric(6)
                #Save OTP
                user_OTP =otp(user=new_userData,otp_code=code)
                user_OTP.save()
                #send_email.send_email("WasteCoin OTP verification",email,' Hello ' + firstName + ",\nWelcome to WasteCoin,"+ "\nYour OTP verification code is: \n " +code + " \nUse this code to verify your registration. WasteCoin will never ask you to share this code with anyone."+ "\n\n Yours Sincerely," + "\n The WasteCoin Team.")
                return_data = {
                    "error": "0",
                    "message":"The registration was successful",
                    "user_id": f"{userRandomId}",
                    "OTP_Code": f"{code}"
                    }
        else:
            return_data = {
                "error":"2",
                "message": "Invalid Parameter"
            }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)

#User verfication
@api_view(["POST"])
@autentication.user_tokenid
def user_verification(request,user_id):
    try:
        otp_entered = request.data.get("otp",None)
        if otp_entered != None and otp_entered != "":
            user_data = otp.objects.get(user__user_id=user_id)
            otpCode,date_added = str(user_data.otp_code),user_data.date_added
            date_now = datetime.now(timezone.utc)
            duration = float((date_now - date_added).total_seconds())
            timeLimit = 1800.0 #30 mins interval
            if otp_entered == otpCode and duration < timeLimit:
                #validate user
                user_data.validated = True
                user_data.save()
                return_data = {
                    "error": "0",
                    "message":"User Verified"
                }
            elif otp_entered != otpCode and duration < timeLimit:
                return_data = {
                    "error": "1",
                    "message": "Incorrect OTP"
                }
            elif otp_entered == otpCode and duration > timeLimit:
                user_data.save()
                return_data = {
                    "error": "1",
                    "message": "OTP has expired"
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameters"
            }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)

#resend OTP
@api_view(["POST"])
def resend_otp(request):
    try:
        email_address = request.data.get('emailaddress',None)
        if email_address != None and email_address != "":
            if User.objects.filter(email =email_address).exists() == False:
                    return_data = {
                        "error": "1",
                        "message": "User does not exist"
                    }
            else:
                user_data = otp.objects.get(user__email=email_address)
                #generate new otp
                code = string_generator.numeric(6)
                user_data.otp_code = code
                user_data.save()
                #send_email.send_email("WasteCoin OTP Re-verification",email_address,' Hello ' + "\nYour OTP Re-verification code is: \n " +code + " \nUse this code to verify your registration. WasteCoin will never ask you to share this code with anyone."+ "\n\n Yours Sincerely," + "\n The WasteCoin Team.")
                return_data = {
                    "error": "0",
                    "message": "OTP sent to mail",
                    "OTP_Code": f"{code}"
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameters"
            }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)

#User login
@api_view(["POST"])
def user_login(request):
    try:
        email_phone = request.data.get("email_phone",None)
        password = request.data.get("password",None)
        field = [email_phone,password]
        if not None in field and not '' in field:
            validate_mail = validator.checkmail(email_phone)
            if validate_mail == True:
                if User.objects.filter(email =email_phone).exists() == False:
                    return_data = {
                        "error": "1",
                        "message": "User does not exist"
                    }
                else:
                    user_data = User.objects.get(email=email_phone)
                    is_valid_password = password_functions.check_password_match(password,user_data.user_password)
                    is_verified = otp.objects.get(user__user_phone=user_data.user_phone).validated
                    if is_valid_password and is_verified:
                        return_data = {
                            "error": "0",
                            "message": "Successfull"
                            }
                    elif is_verified == False:
                        return_data = {
                            "error" : "1",
                            "message": "User is not verified"
                        }
                    else:
                        return_data = {
                            "error" : "1",
                            "message" : "Wrong Password"
                        }
            else:
                if User.objects.filter(user_phone =email_phone).exists() == False:
                    return_data = {
                        "error": "1",
                        "message": "User does not exist"
                    }
                else:
                    user_data = User.objects.get(user_phone=email_phone)
                    is_valid_password = password_functions.check_password_match(password,user_data.user_password)
                    is_verified = otp.objects.get(user__user_phone=user_data.user_phone).validated
                    if is_valid_password and is_verified:
                        return_data = {
                            "error": "0",
                            "message": "Successfull"
                        }
                    elif is_verified == False:
                        return_data = {
                            "error" : "1",
                            "message": "User is not verified"
                        }
                    else:
                        return_data = {
                            "error" : "1",
                            "message" : "Wrong Password"
                        }
        else:
            return_data = {
                "error" : "2",
                "message" : "Invalid Parameters"
                }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)

#send email to change password
@api_view(["POST"])
def password_reset(request):
    try:
        emailAddress = request.data.get('emailaddress',None)
        if emailAddress != None and emailAddress != "":
            if User.objects.filter(email =emailAddress).exists() == False:
                return_data = {
                    "error": "1",
                    "message": "User does not exist"
                }
            else:
                user_data = otp.objects.get(user__email=emailAddress)
                generate_pin = string_generator.alphanumeric(15)
                user_data.otp_reset_code = generate_pin
                user_data.save()
               # send_email.send_email('WasteCoin Reset Password',emailAddress,' Hello ' + "\nYour Reset Password code is: \n " +generate_pin + " \nUse this code to verify your registration. WasteCoin will never ask you to share this code with anyone."+ "\n\n Yours Sincerely," + "\n The WasteCoin Team.")
                return_data = {
                    "error": "0",
                    "message": "Successful, Email sent",
                    "code": f"{generate_pin}"
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameter"
            }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)

#Change password
@api_view(["POST"])
@autentication.user_tokenid
def password_change(request,user_id):
    try:
        reset_code = request.data.get("reset_code")
        new_password = request.data.get("new_password")
        fields = [reset_code,new_password]
        if not None in fields and not "" in fields:
            #get user info
            user_data = User.objects.get(user_id=user_id)
            otp_reset_code = otp.objects.get(user__user_id=user_id).otp_reset_code
            if reset_code == otp_reset_code:
                #encrypt password
                encryptpassword = password_functions.generate_password_hash(new_password)
                user_data.user_password = encryptpassword
                user_data.save()
                return_data = {
                    "error": "0",
                    "message": "Successfull, Password Changed"
                }
            elif resend_otp != otp_reset_code:
                return_data = {
                    "error": "1",
                    "message": "Code does not Match"
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameters"
            }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)