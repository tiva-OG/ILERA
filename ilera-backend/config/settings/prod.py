from .base import *
from decouple import config
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = True

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# DATABASES = {
#     "default": dj_database_url.config(env("DATABASE_URL"), conn_max_age=600),
# }

DATABASES = {"default": dj_database_url.config(default=config("DATABASE_URL"))}
