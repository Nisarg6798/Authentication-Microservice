from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from base.models import Registration, UserOtp
from rest_framework import status
import json
from django.contrib.auth.hashers import make_password, check_password
from twilio.rest import Client
import random
from django.conf import settings
from django.template.loader import render_to_string
from email.mime.text import MIMEText
import smtplib


# Create your views here.


@csrf_exempt
def user_registration(request):
    try:
        if request.method == "POST":
            first_name = request.POST["first_name"] if "first_name" in request.POST else None
            last_name = request.POST["last_name"] if "last_name" in request.POST else None
            email_add = request.POST["email"] if "email" in request.POST else None
            phone_num = request.POST["phone_number"] if "phone_number" in request.POST and len(request.POST["phone_number"]) == 10 else None
            password = request.POST["password"] if "password" in request.POST else None

            enc_password = make_password(password.strip())
            
            if email_add and password and phone_num:
                user_exist = Registration.objects.filter(phone_number=phone_num.strip()).first()
                if not user_exist:
                    Registration.objects.create(first_name=first_name.strip(), last_name=last_name.strip(), email_address=email_add.strip(), phone_number=phone_num, password=enc_password)
                    
                    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    email_from = settings.EMAIL_HOST_USER
                    html_content = render_to_string("email_otp_verification.html", {"otp": otp})
                    text_content = MIMEText(html_content, "html")
                    text_content["Subject"] = "OTP for email verification"
                    text_content["To"] = ",".join(email_add)

                    send_mail(email_from, email_add, text_content)

                    return HttpResponse(json.dumps({"code": 1, "msg": "User is registered!"}), status=status.HTTP_200_OK)
                return HttpResponse(json.dumps({"code": 0, "msg": "Phone number is already exist!"}), status=status.HTTP_400_BAD_REQUEST)
            return HttpResponse(json.dumps({"code": 0, "msg": "`Email address`, `Phone number`, `Password` are invalid!"}), status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(json.dumps({"code": 0, "msg": "Invalid request!"}), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)
    

@csrf_exempt
def send_otp(request):
    try:
        if request.method == "POST":

            phone_num = request.POST["phone_number"] if "phone_number" in request.POST and len(request.POST["phone_number"]) == 10 else None
            if not phone_num:
                return HttpResponse(json.dumps({"code": 0, "msg": "`Phone number` is invalid!"}), status=status.HTTP_400_BAD_REQUEST)
            
            user_exist = Registration.objects.filter(phone_number=phone_num).first()

            if not user_exist:
                return HttpResponse(json.dumps({"code": 0, "msg": "User is not exist with provided phone number!"}), status=status.HTTP_400_BAD_REQUEST)

            account_sid = settings.ACCOUNT_SID
            auth_token = settings.AUTH_TOKEN
            client = Client(account_sid, auth_token)

            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            UserOtp.objects.create(user_id=user_exist.id, otp=otp)

            message = client.messages.create(
                body = f'Your OTP is: {otp}',
                from_ = settings.TWILIO_NUM,  # Your Twilio phone number
                to = '+91' + str(phone_num)
            )
            
            return HttpResponse(json.dumps({"code": 1, "msg": "OTP is sent!"}), status=status.HTTP_200_OK)
        return HttpResponse(json.dumps({"code": 0, "msg": "Invalid request!"}), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)
    

@csrf_exempt
def authcheck(request):
    try:
        if request.method == "POST":
            phone_num = request.POST["phone_number"] if "phone_number" in request.POST and len(request.POST["phone_number"]) == 10 else None
            otp = request.POST["otp"] if "otp" in request.POST and len(request.POST["otp"]) == 6 else None
            if phone_num and otp:
                user_data = UserOtp.objects.filter(user__phone_number=phone_num, otp=otp).first()
                if user_data:
                    return HttpResponse(json.dumps({"code": 1, "msg": "User is authenticated!"}), status=status.HTTP_200_OK)
                return HttpResponse(json.dumps({"code": 1, "msg": "Failed to authenticate!"}), status=status.HTTP_401_UNAUTHORIZED)
            return HttpResponse(json.dumps({"code": 0, "msg": "Invalid `Phone number` or `OTP`!"}), status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(json.dumps({"code": 0, "msg": "Invalid request!"}), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)
    

@csrf_exempt
def send_mail_to_reset_password(request):
    try:
        if request.method == "POST":
            email_add = request.POST["email"] if "email" in request.POST else None
            if email_add:
                user_exist = Registration.objects.filter(email_address=email_add).first()
                if user_exist:

                    email_from = settings.EMAIL_HOST_USER
                    html_content = render_to_string("reset_pwd_link.html", {})
                    text_content = MIMEText(html_content, "html")
                    text_content["Subject"] = "Reset password"
                    text_content["To"] = ",".join(email_add)

                    send_mail(email_from, email_add, text_content)

                    return HttpResponse(json.dumps({"code": 1, "msg": "Check your email to reset password!"}), status=status.HTTP_200_OK)
                return HttpResponse(json.dumps({"code": 1, "msg": "User is not exist!"}), status=status.HTTP_401_UNAUTHORIZED)
            return HttpResponse(json.dumps({"code": 0, "msg": "Invalid `Email address`!"}), status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(json.dumps({"code": 0, "msg": "Invalid request!"}), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)
    

def reset_password_view(request):
    try:
        return render(request, "reset_password.html", {})
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def reset_password(request):
    try:
        if request.method == "POST":
            phone_num = request.POST["phone_number"] if "phone_number" in request.POST and len(request.POST["phone_number"]) == 10 else None
            password = request.POST["password"] if "password" in request.POST else None
            if phone_num and password:
                user_data = Registration.objects.filter(phone_number=phone_num).first()
                if user_data:
                    enc_password = make_password(password.strip())
                    user_data.password = enc_password
                    user_data.save()
                    return HttpResponse(json.dumps({"code": 1, "msg": "Password reset successful!"}), status=status.HTTP_200_OK)
                return HttpResponse(json.dumps({"code": 1, "msg": "User is not exist!"}), status=status.HTTP_401_UNAUTHORIZED)
            return HttpResponse(json.dumps({"code": 0, "msg": "Invalid `Phone number` or `password`!"}), status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(json.dumps({"code": 0, "msg": "Invalid request!"}), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)
    

@csrf_exempt
def update_user_details(request):
    try:
        if request.method == "POST":
            first_name = request.POST["first_name"] if "first_name" in request.POST else None
            last_name = request.POST["last_name"] if "last_name" in request.POST else None
            email_add = request.POST["email"] if "email" in request.POST else None
            phone_num = request.POST["phone_number"] if "phone_number" in request.POST and len(request.POST["phone_number"]) == 10 else None
            password = request.POST["password"] if "password" in request.POST else None
            if email_add:
                user_data = Registration.objects.filter(email_address=email_add).first()
                if user_data:
                    if password:
                        enc_password = make_password(password.strip())
                        user_data.password = enc_password
                    if first_name:
                        user_data.first_name = first_name.strip()
                    if last_name:
                        user_data.last_name = last_name.strip()
                    if phone_num:
                        user_data.phone_number = phone_num
                    user_data.save()
                    return HttpResponse(json.dumps({"code": 1, "msg": "User data is updated!"}), status=status.HTTP_200_OK)
                return HttpResponse(json.dumps({"code": 1, "msg": "User is not exist!"}), status=status.HTTP_401_UNAUTHORIZED)
            return HttpResponse(json.dumps({"code": 0, "msg": "Invalid `email`!"}), status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(json.dumps({"code": 0, "msg": "Invalid request!"}), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)
    

def send_mail(email_from, email_to, text_content=None):
    try:
        server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(email_from, email_to, text_content.as_string())
    except Exception:
        return HttpResponse(json.dumps({"code": 0, "msg": "Internal Error!"}), status=status.HTTP_404_NOT_FOUND)