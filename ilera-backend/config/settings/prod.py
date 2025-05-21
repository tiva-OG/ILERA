from .base import *

DEBUG = False
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = False

MIDDLEWARE += [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DATABASES = {
    "default": dj_database_url.config(env("DATABASE_URL"), conn_max_age=600),
}
