import datetime

import jwt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import User, UserCoins, UserTrasactionHistory, otp, AccountDetails
from CustomCode import (autentication, fixed_var, password_functions,
                        string_generator, validator,sms)
from wasteCoin import settings


# Create your views here.
@api_view(['GET'])
def index_page(request):
    return_data = {
        "error" : "0",
        "message" : "Successful"
    }
    return Response(return_data)

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
                miner_id = string_generator.numeric(7)
                transactionid = string_generator.alphanumeric(15)
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
                #Generate default coins
                user_Coins = UserCoins(user=new_userData,minerID=miner_id,allocateWasteCoin=0,minedCoins=0)
                user_Coins.save()
                #Save Transaction Details
                user_transaction = UserTrasactionHistory(user=new_userData,transaction_id=transactionid,
                                                        amount=0,coin_mined_amount=0,coin_allocated_to=miner_id,transaction="Credit")
                user_transaction.save()
                role = User.objects.get(user_id=userRandomId).role
                #Generate token
                timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set limit for user
                payload = {"user_id": f"{userRandomId}",
                           "role": role,
                           "exp":timeLimit}
                token = jwt.encode(payload,settings.SECRET_KEY)
                message = f"Welcome to WasteCoin, your verification code is {code}"
                sms.sendsms(phoneNumber[1:],message)
                return_data = {
                    "error": "0",
                    "message": "The registration was successful, A verrification SMS has been sent",
                    "token": f"{token.decode('UTF-8')}",
                    "elapsed_time": f"{timeLimit}",
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
@autentication.token_required
def user_verification(request,decrypedToken):
    try:
        otp_entered = request.data.get("otp",None)
        if otp_entered != None and otp_entered != "":
            user_data = otp.objects.get(user__user_id=decrypedToken['user_id'])
            otpCode,date_added = user_data.otp_code,user_data.date_added
            date_now = datetime.datetime.now(datetime.timezone.utc)
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
        phone_number = request.data.get('phone_number',None)
        if phone_number != None and phone_number != "":
            if User.objects.filter(user_phone =phone_number).exists() == False:
                    return_data = {
                        "error": "1",
                        "message": "User does not exist"
                    }
            else:
                user_data = otp.objects.get(user__user_phone=phone_number)
                #generate new otp
                code = string_generator.numeric(6)
                user_data.otp_code = code
                user_data.save()
                message = f"Welcome to WasteCoin, your verification code is {code}"
                sms.sendsms(phone_number[1:],message)
                return_data = {
                    "error": "0",
                    "message": "OTP sent to phone number"
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
                    #Generate token
                    timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set limit for user
                    payload = {"user_id": f'{user_data.user_id}',
                               "role": user_data.role,
                               "exp":timeLimit}
                    token = jwt.encode(payload,settings.SECRET_KEY)
                    if is_valid_password and is_verified:
                        return_data = {
                            "error": "0",
                            "message": "Successfull",
                            "token": token.decode('UTF-8'),
                            "token-expiration": f"{timeLimit}",
                            "user_details": [
                                {
                                    "firstname": f"{user_data.firstname}",
                                    "lastname": f"{user_data.lastname}",
                                    "email": f"{user_data.email}",
                                    "phone_number": f"{user_data.user_phone}",
                                    "gender": f"{user_data.user_gender}",
                                    "address": f"{user_data.user_address}",
                                    "state": f"{user_data.user_state}",
                                    "LGA": f"{user_data.user_LGA}",
                                    "country": f"{user_data.user_country}"

                                }
                            ]

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
                    is_verified = otp.objects.get(user__user_phone=user_data.user_phone).validated
                    is_valid_password = password_functions.check_password_match(password,user_data.user_password)
                    #Generate token
                    timeLimit= datetime.datetime.utcnow() + datetime.timedelta(minutes=1440) #set limit for user
                    payload = {"user_id": f'{user_data.user_id}',
                               "role": user_data.role,
                               "exp":timeLimit}
                    token = jwt.encode(payload,settings.SECRET_KEY)
                    if is_valid_password and is_verified:
                        return_data = {
                            "error": "0",
                            "message": "Successfull",
                            "token": token.decode('UTF-8'),
                            "token-expiration": f"{timeLimit}",
                            "user_details": [
                                {
                                    "firstname": f"{user_data.firstname}",
                                    "lastname": f"{user_data.lastname}",
                                    "email": f"{user_data.email}",
                                    "phone_number": f"{user_data.user_phone}",
                                    "gender": f"{user_data.user_gender}",
                                    "address": f"{user_data.user_address}",
                                    "state": f"{user_data.user_state}",
                                    "LGA": f"{user_data.user_LGA}",
                                    "country": f"{user_data.user_country}"

                                }
                            ]

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


@api_view(["POST"])
def password_reset(request):
    try:
        phone_number = request.data.get('phone_number',None)
        if phone_number != None and phone_number != "":
            if User.objects.filter(user_phone =phone_number).exists() == False:
                return_data = {
                    "error": "1",
                    "message": "User does not exist"
                }
            else:
                user_data = otp.objecttransaction_ids.get(user__user_phone=phone_number)
                generate_pin = string_generator.alphanumeric(15)
                user_data.password_reset_code = generate_pin
                user_data.save()
                message = f"Welcome to WasteCoin, your password reset code is {generate_pin}"
                sms.sendsms(phone_number[1:],message)
                return_data = {
                    "error": "0",
                    "message": "Successful, reset code sent to Phone Number",
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameter"
            }
    except Exception as e:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)

#Change password
@api_view(["POST"])
@autentication.token_required
def password_change(request,decrypedToken):
    try:
        reset_code = request.data.get("reset_code",None)
        new_password = request.data.get("new_password",None)
        fields = [reset_code,new_password]
        if not None in fields and not "" in fields:
            #get user info
            user_data = User.objects.get(user_id=decrypedToken["user_id"])
            otp_reset_code = otp.objects.get(user__user_id=decrypedToken["user_id"]).password_reset_code
            print(otp_reset_code)
            if reset_code == otp_reset_code:
                #encrypt password
                encryptpassword = password_functions.generate_password_hash(new_password)
                user_data.user_password = encryptpassword
                user_data.save()
                return_data = {
                    "error": "0",
                    "message": "Successfull, Password Changed"
                }
            elif reset_code != otp_reset_code:
                return_data = {
                    "error": "1",
                    "message": "Code does not Match"
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameters"
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)

@api_view(["GET"])
@autentication.token_required
def Dashboard(request,decrypedToken):
    try:
        user_id = decrypedToken['user_id']
        if user_id != None and user_id != '':
            user_data = UserCoins.objects.get(user__user_id=user_id)
            user_coins = user_data.allocateWasteCoin
            month = user_data.date_added.strftime('%B')
            rate_exchange = fixed_var.exchange_rate
            rate_changed = fixed_var.changed_rate
            exchangeRate,changed_rate = rate_exchange,rate_changed
            minedCoins = user_data.minedCoins
            unminedCoins = user_coins - minedCoins
            WasteCoinBoard = UserCoins.objects.all().order_by('-minedCoins')
            i = 0
            topCoinsMined = []
            #numberOfUsers = 5
            while i < len(WasteCoinBoard):
                topUsers = {
                    "miner_id": WasteCoinBoard[i].minerID,
                    "CoinMined": UserCoins.objects.get(user__user_id=WasteCoinBoard[i].user.user_id).minedCoins
                }
                topCoinsMined.append(topUsers)
                i += 1
            if decrypedToken['role'] == "user":
                return_data = {
                    "error": "0",
                    "message": "Sucessfull",
                    "data":
                        {
                            "allocatedWasteCoin": user_coins,
                            "month": month,
                            "exchangeRate": exchangeRate,
                            "changedRate": changed_rate,
                            "summary": {
                                "mined": minedCoins,
                                "unMined": unminedCoins
                            },
                            "totalWasteCoinMined": minedCoins,
                            "leaderBoard": topCoinsMined
                    }
            }
            else:
                return_data = {
                    "error": "0",
                    "message": "Sucessfull",
                    "data":
                        {
                            "allocatedWasteCoin": user_coins,
                            "month": month,
                            "exchangeRate": exchangeRate,
                            "changedRate": changed_rate
                    }
            }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameter"
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)

#Check leaderboard
@api_view(["GET"])
def LeadBoard(request):
    try:
        WasteCoinBoard = UserCoins.objects.all().order_by('-minedCoins')
        i = 0
        topCoinsMined = []
        #numberOfUsers = 2
        while i < len(WasteCoinBoard):
            topUsers = {
                "miner_id": WasteCoinBoard[i].minerID,
                "CoinMined": UserCoins.objects.get(user__user_id=WasteCoinBoard[i].user.user_id).minedCoins
            }
            topCoinsMined.append(topUsers)
            i += 1
        return_data = {
            "error": "0",
            "message": "Successfull",
            "LeaderBoard": topCoinsMined
        }
    except Exception:
        return_data = {
            "error": "3",
            "message": str(e)
        }
    return Response(return_data)

@api_view(["GET"])
@autentication.token_required
def user_profile(request,decrypedToken):
    try:
        userID = decrypedToken['user_id']
        UserInfo = User.objects.get(user_id=userID)
        UserCoin = UserCoins.objects.get(user__user_id=userID)
        #verify if user have account
        account_info = AccountDetails.objects.filter(user__user_id=decrypedToken['user_id']).exists()
        if account_info == True:
            account = AccountDetails.objects.get(user__user_id=decrypedToken['user_id'])
            account_details = {
                "account_name": account.account_name,
                "account_number": account.account_number,
                "bank_name": account.bank_name
            }
        else:
            account_details = {
                "account_name": "null",
                "account_number": "null",
                "bank_name": "null"
            }
        return_data = {
            "error": "0",
            "message": "Successfull",
            "data": {
                    "user_details": {
                            "first_name": f"{UserInfo.firstname}",
                            "last_name": f"{UserInfo.lastname}",
                            "email": f"{UserInfo.email}",
                            "phone_number": f"{UserInfo.user_phone}",
                            "gender": f"{UserInfo.user_gender}",
                            "address": f"{UserInfo.user_address}",
                            "state": f"{UserInfo.user_state}",
                            "LGA": f"{UserInfo.user_LGA}",
                            "country": f"{UserInfo.user_country}",
                            "role": f"{UserInfo.role}"

                        }
                    ,
                    "user_coins": {
                            "miner_id": f"{UserCoin.minerID}",
                            "allocatedCoin": f"{UserCoin.allocateWasteCoin}",
                            "minedcoins": f"{UserCoin.minedCoins}"
                        },
                    "account_information": account_details

                }

        }

    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)

@api_view(["GET"])
@autentication.token_required
def wallet_details(request,decrypedToken):
    try:
        userID = decrypedToken['user_id']
        user_coins = UserCoins.objects.get(user__user_id=userID)
        transaction_history = UserTrasactionHistory.objects.filter(user__user_id=userID)
        numOfTransactions = len(transaction_history)
        trasactions = []
        if decrypedToken["role"] == "user":
            i = 0
            while i < numOfTransactions:
                perTransaction = {
                    "date": transaction_history[i].date_added.strftime("%Y-%m-%d"),
                    "amount": transaction_history[i].amount,
                    "transaction": transaction_history[i].transaction
                }
                trasactions.append(perTransaction)
                i += 1
            return_data = {
                "error": "0",
                "message": "Successfull",
                "data": {
                    "current_balance": f"{user_coins.allocateWasteCoin}",
                    "transaction_history": trasactions[1:]
                }
            }
        else:
            i = 0
            while i < numOfTransactions:
                perTransaction = {
                    "date": transaction_history[i].date_added.strftime("%Y-%m-%d"),
                    "amount": transaction_history[i].amount,
                    "miner_id": transaction_history[i].coin_allocated_to
                }
                trasactions.append(perTransaction)
                i +=1
            return_data = {
                "error": "0",
                "message": "Successfull",
                "data": {
                    "current_balance": f"{user_coins.allocateWasteCoin}",
                    "transaction_history": trasactions[1:]
                }
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)

@api_view(["POST"])
@autentication.token_required
def redeemcoins(request,decrypedToken):
    try:
        coins_amount = request.data.get("amount",None)
        if coins_amount != None and coins_amount != "":
            coins_amount = float(coins_amount)
            if coins_amount == float(0) or coins_amount < float(0):
                return_data = {
                    "error": 2,
                    "message": "Number is negative or zero"
                }
            else:
                user_coins = UserCoins.objects.get(user__user_id=decrypedToken["user_id"])
                exchange_rate = fixed_var.exchange_rate
                numofCoins = user_coins.allocateWasteCoin
                user_data = User.objects.get(user_id=decrypedToken["user_id"])
                if coins_amount > numofCoins:
                    return_data = {
                        "error": "1",
                        "message": "Not enough coins"
                    }
                else:
                    transactionid = string_generator.alphanumeric(15)
                    toNaira = exchange_rate * coins_amount
                    user_coins.allocateWasteCoin = numofCoins - coins_amount
                    user_coins.minedCoins = coins_amount
                    user_coins.save()
                    #Save Transaction
                    transaction = UserTrasactionHistory(user=user_data,transaction_id=transactionid,
                                      amount=coins_amount,coin_mined_amount=toNaira,coin_allocated_to=user_coins.minerID,transaction="Debit")
                    transaction.save()
                    #Add coin to the coin repository
                    return_data = {
                        "error": "0",
                        "message": "Successful, Coin Mined",
                        "transaction_id": f"{transactionid}",
                        "amount": f"{toNaira}"
                    }
        else:
            return_data = {
                "error": 2,
                "message": "Invalid Parameter"
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)



@api_view(["POST"])
@autentication.token_required
def allocate_coins(request,decrypedToken):
    try:
        coins_allocated = float(request.data.get("coins_allocated",None))
        user_MinerID = request.data.get("miner_id",None)
        field = [coins_allocated,user_MinerID]
        if not None in field and not "" in field:
            if UserCoins.objects.filter(minerID=user_MinerID).exists() == False:
                return_data = {
                    "error": "1",
                    "message": "User does not exist"

                    }

            elif User.objects.get(user_id= decrypedToken['user_id']).role != "agent":
                return_data = {
                    "error": "2",
                    "message": "Unauthorized User"

                    }
            else:
                agent_coins = UserCoins.objects.get(user__user_id=decrypedToken["user_id"]).allocateWasteCoin
                if coins_allocated > agent_coins:
                    return_data = {
                        "error": "2",
                        "message": "Not enough coins"
                    }
                else:
                    wastecoin_user = UserCoins.objects.get(minerID=user_MinerID)
                    user = wastecoin_user.user
                    agent_user = User.objects.get(user_id= decrypedToken['user_id'])
                    agent_coins = UserCoins.objects.get(user__user_id=decrypedToken["user_id"])
                    user_coins = UserCoins.objects.get(user__user_id=user.user_id)
                    string_generator.alphanumeric(15)
                    #allocate Coin to user
                    remaining_coins =agent_coins.allocateWasteCoin - coins_allocated
                    agent_coins.allocateWasteCoin = remaining_coins
                    #Debit_agent
                    withdrawl= UserTrasactionHistory(user=agent_user,transaction_id=string_generator.alphanumeric(15),amount=coins_allocated,
                                                     coin_mined_amount=0,coin_allocated_to=user_MinerID,transaction="Debit")
                    agent_coins.save()
                    withdrawl.save()
                    #credit User
                    add_coins = user_coins.allocateWasteCoin + coins_allocated
                    user_coins.allocateWasteCoin = add_coins
                    allocate = UserTrasactionHistory(user=user,transaction_id=string_generator.alphanumeric(15),amount=coins_allocated,
                                                     coin_mined_amount=0,coin_allocated_to=user_MinerID,transaction="Credit")
                    user_coins.save()
                    allocate.save()
                    return_data = {
                        "error": "0",
                        "message": f"Successful,coins allocated to {user.firstname} {user.lastname}"
                    }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameters"
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
            }
    return Response(return_data)


@api_view(["POST"])
@autentication.token_required
def changepassword(request,decryptedToken):
    try:
        old_password = request.data.get("old_password",None)
        new_password = request.data.get("new_password",None)
        field = [old_password,new_password]
        if not None in field and not "" in field:
            user_data = User.objects.get(user_id=decryptedToken["user_id"])
            is_valid_password = password_functions.check_password_match(old_password,user_data.user_password)
            if is_valid_password == False:
                return_data = {
                    "error": "2",
                    "message": "Password is Incorrect"
                }
            else:
                #decrypt password
                encryptpassword = password_functions.generate_password_hash(new_password)
                user_data.user_password = encryptpassword
                user_data.save()
                return_data = {
                    "error": "0",
                    "message": "Successfull, Password Changed"
                }
    except Exception:
        return_data = {
                "error": "3",
                "message": "An error occured"
        }
    return Response(return_data)

@api_view(["PUT"])
@autentication.token_required
def update_info(request,decryptedToken):
    try:
        address = request.data.get("address",None)
        state = request.data.get("state",None)
        user_lga = request.data.get("lga",None)
        field = [address,state,user_lga]
        if not None in field and not "" in field:
            print(decryptedToken["user_id"])
            user_data = User.objects.get(user_id=decryptedToken["user_id"])
            user_data.user_address = address
            user_data.user_state = state
            user_data.user_LGA = user_lga
            user_data.save()
            return_data = {
                "error": "0",
                "message": "Successfully Updated",
                "data": {
                    "address": address,
                    "state": state,
                    "lga": user_lga
                }
            }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameter"
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)

@api_view(["POST","PUT"])
@autentication.token_required
def account_details(request,decryptedToken):
    try:
        accountName = request.data.get("account_name",None)
        accountNumber = request.data.get("account_number",None)
        bankName = request.data.get("bank_name",None)
        field = [accountName,accountNumber,bankName]
        if not None in field and not "" in field:
            user_data = User.objects.get(user_id=decryptedToken['user_id'])
            if AccountDetails.objects.filter(user__user_id=decryptedToken['user_id']).exists():
                user_account = AccountDetails.objects.get(user__user_id=decryptedToken['user_id'])
                user_account.account_number = accountNumber
                user_account.account_name = accountName
                user_account.bank_name = bankName
                user_account.save()
                return_data = {
                    "error": "0",
                    "message": "Account saved successfully",
                    "data": {
                        "account_name": accountName,
                        "account_number": accountNumber,
                        "bank_name": bankName
                    }
                }
            else:
                user_account = AccountDetails(user=user_data,account_name=accountName,
                                              account_number=accountNumber,bank_name=bankName)
                user_account.save()
                return_data = {
                    "error": "0",
                    "message": "Account saved successfully",
                    "data": {
                        "account_name": accountName,
                        "account_number": accountNumber,
                        "bank_name": bankName
                    }
                }
        else:
            return_data = {
                "error": "2",
                "message": "Invalid Parameter"
            }
    except Exception:
        return_data = {
            "error": "3",
            "message": "An error occured"
        }
    return Response(return_data)