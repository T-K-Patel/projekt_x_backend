# import pyrebimport firebase_admin
import firebase_admin
from firebase_admin import credentials, storage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from projekt_x_backend.settings import FIREBASE_CONFIG
try:
    from projekt_x_backend.settings import EMAIL_HOST_USER
except:
    EMAIL_HOST_USER = "noreply.projekt.x.team@gmail.com"
    


cred = credentials.Certificate(FIREBASE_CONFIG)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'projekt-x-402611.appspot.com'
})
bucket = storage.bucket()


def upload_profile(profile_photo, filename,prev=None):
    type = profile_photo.content_type
    blob = bucket.blob(filename)
    blob.content_type = type
    blob.upload_from_file(profile_photo)
    blob.make_public()
    url = blob.public_url
    if prev:
        try:
            blob = bucket.blob(prev)
            blob.make_private()
        except:
            print(f"Error making {prev} private")
    return url


def send_reset_email(context, email="johnny.x.mia@gmail.com"):
    html_content = render_to_string(
        'Mailer/reset_password_mail_template.html', context=context)
    text_content = strip_tags(html_content)
    return send_mail(
        subject="Reset Password link for Projekt-X Account",
        from_email=f"Projekt-X Team <{EMAIL_HOST_USER}>",
        message=text_content,
        recipient_list=[email],
        html_message=html_content,
        # fail_silently=True
    )


def send_reg_email(context, email="johnny.x.mia@gmail.com"):
    html_content = render_to_string(
        'Mailer/registration_success.html', context=context)
    text_content = strip_tags(html_content)
    return send_mail(
        subject="Registration Successful on Projekt-X",
        from_email=f"Projekt-X Team <{EMAIL_HOST_USER}>",
        message=text_content,
        recipient_list=[email],
        html_message=html_content,
        # fail_silently=True
    )
