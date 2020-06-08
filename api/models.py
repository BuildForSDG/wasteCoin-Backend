from django.db import models
from django.utils import timezone

# Create your models here.
class User(models.Model):
    class Meta:
        db_table = "WasteCoin_user_table"
    user_id = models.CharField(max_length=500,unique=True)
    firstname = models.CharField(max_length=30,verbose_name="Firstname",blank=True)
    lastname = models.CharField(max_length=30,verbose_name="Lastname",blank=True)
    email = models.EmailField(max_length=90, unique=True,verbose_name="Email")
    user_phone = models.CharField(max_length=15, unique=True, null=True, verbose_name="Telephone number")
    user_gender = models.CharField(max_length=15, verbose_name="Gender")
    user_password = models.TextField(max_length=200,verbose_name="Password")
    user_address = models.TextField(max_length=200,verbose_name="Address")
    user_state = models.TextField(max_length=200,verbose_name="State")
    user_LGA = models.TextField(max_length=200,verbose_name="State")
    user_country = models.TextField(max_length=200,verbose_name="Country")
    date_added = models.DateTimeField(default=timezone.now)
    role = models.TextField(max_length=50,verbose_name="User role",default="user")

class otp(models.Model):
    class Meta:
        db_table = "OTP_Code"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.TextField(max_length=20,verbose_name="OTP CODE")
    validated = models.BooleanField(default=False)
    password_reset_code = models.TextField(max_length=20,verbose_name="Reset Code",default="")
    date_added = models.DateTimeField(default=timezone.now)


class UserCoins(models.Model):
    class Meta:
        db_table = "User_Coins"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    minerID = models.CharField(max_length=500,unique=True,verbose_name="miner_ID")
    redeemedWasteCoin = models.FloatField(verbose_name="redeemedWasteCoin",default=0)
    minedCoins = models.FloatField(verbose_name="minedCoins",default=0)
    date_added = models.DateTimeField(default=timezone.now)

class AgentCoins(models.Model):
    class Meta:
        db_table = "Agent_Coins"
    agent = models.ForeignKey(User,on_delete=models.CASCADE)
    agentCoins = models.FloatField(verbose_name="AllocatedCoins",default=0)
    date_added = models.DateTimeField(default=timezone.now)

class UserTrasactionHistory(models.Model):
    class Meta:
        db_table = "User_Transaction_History"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.TextField(verbose_name="trans_id",unique=True)
    amount = models.FloatField(verbose_name="CoinAmount")
    coin_redeemed_amount = models.FloatField(verbose_name="CoinunminedAmount",default=0)
    transaction = models.TextField(max_length=10,verbose_name="Transactions")
    date_added = models.DateTimeField(default=timezone.now)

class AgentTransactionHistory(models.Model):
    class Meta:
        db_table = "Agent_Transaction_History"
    agent = models.ForeignKey(User,on_delete=models.CASCADE)
    transaction_id = models.TextField(verbose_name="trans_id",unique=True)
    amount = models.FloatField(verbose_name="CoinAmount")
    coin_allocated_to = models.TextField(verbose_name="Miner_ID",default=0)
    transaction = models.TextField(max_length=10,verbose_name="Transactions")
    date_added = models.DateTimeField(default=timezone.now)

class AccountDetails(models.Model):
    class Meta:
        db_table = "Account Details"
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    account_name = models.TextField(max_length=150,unique=True,verbose_name="Account Name")
    account_number = models.TextField(max_length=150,unique=True,verbose_name="Account Number")
    bank_name = models.TextField(max_length=150,verbose_name="Bank Name")
    date_added = models.DateTimeField(default=timezone.now)

class ContactUs(models.Model):
    class Meta:
        db_table = "Contact Us"
    full_name = models.TextField(verbose_name="Full_Name")
    email = models.TextField(max_length=200,verbose_name="email")
    phone_number = models.TextField(max_length=20,verbose_name="phone_number",default="")
    message = models.TextField(verbose_name="message")
    date_added = models.DateTimeField(default=timezone.now)