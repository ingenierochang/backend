




import os





# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = ['*']

SECRET_KEY = str(os.environ.get("SECRET_KEY"))



# we need this for s3 deploy
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
}

# DATABASES
DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.postgresql',
        'NAME':str(os.environ.get("AWS_POSTGRES_DATABASE")),
        'USER': str(os.environ.get("AWS_POSTGRES_USER")),
        'PASSWORD': str(os.environ.get("AWS_POSTGRES_PASSWORD")),
        'HOST':str(os.environ.get("AWS_POSTGRES_HOST")),
        'PORT':'5432'
    }
}

# HTTPS settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True


# HSTS settings
SECURE_HSTS_SECONDS = 31536000 # 1 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True


HOST_PROTOCOL = 'http://'

# # we need this for s3 
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3StaticStorage"},
}


# # # S3 BUCKETS CONFIG
AWS_IAM_ACCESS_KEY = str(os.environ.get("AWS_S3_ACCESS_KEY_ID"))
AWS_IAM_SECRET_KEY = str(os.environ.get("AWS_S3_SECRET_ACCESS_KEY"))
