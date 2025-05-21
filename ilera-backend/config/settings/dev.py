# environment specific settings
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = False
