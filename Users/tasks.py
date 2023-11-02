# import pyrebase

import uuid
import firebase_admin
from firebase_admin import auth, credentials, storage
import os
from dotenv import load_dotenv

load_dotenv()

firebase_config = {
    "type": os.environ.get("FIREBASE_TYPE"),
    "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": os.environ.get("FIREBASE_AUTH_URI"),
    "token_uri": os.environ.get("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.environ.get("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_config)

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
