from django.db import models

# Create your models here.


class Registration(models.Model):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email_address = models.EmailField(null=False, blank=False)
    phone_number = models.IntegerField(null=False, blank=False)
    password = models.CharField(max_length=50, null=False, blank=False)
    created_on = models.DateTimeField(auto_now_add=True)


class UserOtp(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.PROTECT)
    otp = models.IntegerField(null=False, blank=False)
    is_otp_expired = models.BooleanField(default=False)