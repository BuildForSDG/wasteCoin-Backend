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

class otp(models.Model):
    class Meta:
        db_table = "OTP_Code"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.IntegerField(verbose_name="OTP",blank=False)
    validated = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    otp_reset_code = models.TextField(max_length=20,verbose_name="Reset Code",default="")
