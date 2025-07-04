import os
import threading
from django.apps import AppConfig
from django.conf import settings


class SensorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sensors"

    def ready(self):
        from . import signals

        """
        Spawn the mock‑sensor thread when Django boots,
        *only* if we’re in dev / staging and only once.
        """
        # 1.  Avoid spawning twice when `runserver` does its reloader dance
        if os.environ.get("RUN_MAIN") != "true":
            return

        # 2.  Skip entirely in production unless you deliberately enable it
        # if not getattr(settings, "ENABLE_MOCK_SENSORS", settings.DEBUG):
        #     return

        # 3.  Import here to avoid Django‑app registry issues
        from .mock_http_loop import run_forever

        t = threading.Thread(
            target=run_forever,
            name="MockSensorLoop",
            daemon=True,  # dies with the main process
        )
        t.start()
        print("[SensorsConfig] 🚀 mock‑sensor thread started")
