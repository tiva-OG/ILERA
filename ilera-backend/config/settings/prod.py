from .base import *
from decouple import config
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
# ALLOWED_HOSTS = ["*"]

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
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL")],
        },
    }
}
