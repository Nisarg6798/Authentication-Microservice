# Authentication-Microservice
Note - To get otp on mobile number you need to set your twilio 'ACCOUNT_SID', 'AUTH_TOKEN' and 'TWILIO_NUM in settings.py, To get email you need to set your 'EMAIL_HOST_USER' and EMAIL_HOST_PASSWORD' in settings.py.

Project Api's:
1. User Registration:
   url - http://127.0.0.1:8000/registration/
   post data -
    first_name:Nisarg
    last_name:Prajapati
    email:nisarg@gmail.com
    phone_number:1234567890
    password:123456
2. User Login with OTP:
   1. Send otp to phone number:
      url - http://127.0.0.1:8000/send_otp/
      post data - phone_number:1234567890
   2. Authenticate with otp:
      url - http://127.0.0.1:8000/authcheck/
      post data -
        phone_number:1234567890
        otp:123456
3. Password Reset:
   url - http://127.0.0.1:8000/send_mail_to_reset_password/
   post data - email:nisarg06798@gmail.com
   note - Reset password link is provided in mail.
4. Account Information Update:
   url - http://127.0.0.1:8000/update_user_details/
   post data -
    first_name:Nisarg p
    last_name:Prajapati
    email:nisarg@gmail.com
    phone_number:1234567890
    password:123456
