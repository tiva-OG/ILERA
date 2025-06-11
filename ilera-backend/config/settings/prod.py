from .base import *
from decouple import config
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
# ALLOWED_HOSTS = ["*"]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = True

INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUD_NAME"),
    "API_KEY": env("CLOUD_API_KEY"),
    "API_SECRET": env("CLOUD_API_SECRET"),
}


MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# DATABASES = {
#     "default": dj_database_url.config(env("DATABASE_URL"), conn_max_age=600),
# }

DATABASES = {"default": dj_database_url.config(default=config("DATABASE_URL"))}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL")],
        },
    }
}
