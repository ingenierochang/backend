INSTALLED_APPS = [
    ...,
    "corsheaders",
    "rest_framework",
    ...
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...,
]
ALLOWED_HOSTS = ["api.grupolm.cloud"]
CORS_ALLOWED_ORIGINS = [
    "https://dashboard.grupolm.cloud",
    "https://menu.grupolm.cloud",
]
