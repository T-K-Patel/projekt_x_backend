# import pyrebimport firebase_admin
import firebase_admin
from firebase_admin import credentials, storage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from projekt_x_backend.settings import FIREBASE_CONFIG


cred = credentials.Certificate(FIREBASE_CONFIG)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'projekt-x-402611.appspot.com'
})
bucket = storage.bucket()


def upload_profile(profile_photo, filename, to_delete=None):
    blob = bucket.blob(filename)
    blob.upload_from_file(profile_photo)
    blob.make_public()
    if to_delete:
        try:
            blob = bucket.blob(to_delete)
            blob.delete()
        except:
            print("Delete Error for " + to_delete)
    return blob.public_url


def send_reset_email(context, email="johnny.x.mia@gmail.com"):
    html_content = render_to_string(
        'Mailer/reset_password_mail_template.html', context=context)
    text_content = strip_tags(html_content)
    return send_mail(
        subject="Reset Password link for Projekt-X Account",
        from_email="Projekt-X Team <tk.web.mail.madana@gmail.com>",
        message=text_content,
        recipient_list=[email],
        html_message=html_content,
        fail_silently=True
    )


def send_reg_email(context, email="johnny.x.mia@gmail.com"):
    html_content = render_to_string(
        'Mailer/registration_success.html', context=context)
    text_content = strip_tags(html_content)
    return send_mail(
        subject="Registration Successful on Projekt-X",
        from_email="Projekt-X Team <tk.web.mail.madana@gmail.com>",
        message=text_content,
        recipient_list=[email],
        html_message=html_content,
        fail_silently=True
    )
