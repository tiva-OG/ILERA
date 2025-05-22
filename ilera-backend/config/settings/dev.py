# environment specific settings
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = False


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
