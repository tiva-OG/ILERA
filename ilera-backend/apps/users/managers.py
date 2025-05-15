from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    User model manager with phone-number as the unique identifier for authentication instead of username
    """

    def create_user(self, phone, password=None, **kwargs):
        if not phone:
            raise ValueError(_("User phone number must be set."))

        phone = self.normalize_nigerian_phone(phone)
        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone, password=None, **kwargs):
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_active", True)
        kwargs.setdefault("role", "admin")

        return self.create_user(phone, password, **kwargs)

    def normalize_nigerian_phone(self, phone):
        phone = phone.strip().replace(" ", "")
        if phone.startswith("0") and len(phone) == 11:
            return "+234" + phone[1:]
        return phone
