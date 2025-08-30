









import os
from dotenv import load_dotenv
load_dotenv()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ['*']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')





from .base import BASE_DIR
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# # DATABASES
# DATABASES = {
#     'default':{
#         'ENGINE':'django.db.backends.postgresql',
#         'NAME':str(os.environ.get("AWS_POSTGRES_DATABASE")),
#         'USER': str(os.environ.get("AWS_POSTGRES_USER")),
#         'PASSWORD': str(os.environ.get("AWS_POSTGRES_PASSWORD")),
#         'HOST':str(os.environ.get("AWS_POSTGRES_HOST")),
#         'PORT':'5432'
#     }
# }





# # we need this for s3 
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
}


# # # S3 BUCKETS CONFIG
AWS_IAM_ACCESS_KEY = os.getenv("AWS_S3_ACCESS_KEY_ID")
AWS_IAM_SECRET_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
