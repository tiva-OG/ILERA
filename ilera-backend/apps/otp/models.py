from django.db import models
from django.utils import timezone


class OTPRequest(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "OTP Request"
        indexes = [
            models.Index(fields=["phone", "code"]),
        ]
        ordering = ["-created_at"]

    def is_expired(self, expiry_minutes=5):
        return self.created_at < (timezone.now() - timezone.timedelta(minutes=expiry_minutes))

    def __str__(self):
        return f"OTP [{self.code}] for {self.phone} ({'verified' if self.is_verified else 'pending'})"
