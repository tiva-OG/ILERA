from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification
from apps.livestock.models import HealthStatus
from apps.notifications.models import NotificationType
from apps.notifications.serializers import NotificationSerializer
from apps.vetcare.models import SessionStatus


class VetcareNotificationDispatcher:
    def __init__(self, session):
        self.session = session
        self.status = session.status
        self.has_history = session.has_history

        self.vet = session.vet.user
        self.farmer = session.farmer.user
        self.vet_name = self.vet.get_fullname()
        self.farmer_name = self.farmer.get_fullname()

        self.metadata = {
            "farmer_id": self.farmer.id,
            "vet_id": self.vet.id,
            "session_id": session.id,
        }

    def dispatch(self):
        if self.status == SessionStatus.PENDING:
            self._notify_request_sent()

        elif self.status == SessionStatus.ACCEPTED:
            self._notify_request_accepted()

        elif self.status == SessionStatus.DECLINED:
            self._notify_request_declined()

        elif self.status is None and self.has_history:
            self._notify_session_concluded()

        # Easily add more:
        # elif self.status == SessionStatus.CANCELLED:
        #     self._notify_cancelled()

    def _send(self, actor, receiver, type, title, body, notify_ws=True):
        notification = Notification.objects.create(
            type=type,
            title=title,
            body=body,
            actor=actor,
            receiver=receiver,
            metadata=self.metadata,
        )

        if notify_ws:
            self._send_ws_notification(notification)

    def _send_ws_notification(self, notification):
        channel_layer = get_channel_layer()
        group_name = f"user_{notification.receiver.id}"

        payload = NotificationSerializer(notification).data

        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "notify", "notification": payload},
        )

    def _notify_request_sent(self):
        self._send(
            actor=self.farmer,
            receiver=self.vet,
            type=NotificationType.CARE_REQUEST_SENT,
            title="New Vetcare Request",
            body=f"You have a new service request from {self.farmer_name} for livestock support.",
        )

    def _notify_request_accepted(self):
        self._send(
            actor=self.vet,
            receiver=self.farmer,
            type=NotificationType.CARE_REQUEST_ACCEPTED,
            title="Vetcare Request Accepted",
            body=f"Dr. {self.vet_name} accepted your request for livestock support.",
        )

    def _notify_request_declined(self):
        self._send(
            actor=self.vet,
            receiver=self.farmer,
            type=NotificationType.CARE_REQUEST_DECLINED,
            title="Vetcare Request Declined",
            body=f"Dr. {self.vet_name} seems unavailable right now. Make a request to another available vet.",
        )

    def _notify_session_concluded(self):
        body = f"The session between {self.farmer_name} and Dr. {self.vet_name} has concluded."

        self._send(
            actor=self.farmer,
            receiver=self.vet,
            type=NotificationType.CARE_REQUEST_CONCLUDED,
            title="Vetcare Session Concluded",
            body=body,
        )
        self._send(
            actor=self.vet,
            receiver=self.farmer,
            type=NotificationType.CARE_REQUEST_CONCLUDED,
            title="Vetcare Session Concluded",
            body=body,
        )


class NotificationService:
    # TIMESTAMP = datetime.now().strftime("%b %d, %Y at %l:%M %p")

    # Vet gets notified when: Farmer requests service; terminates service
    # Farmer gets notified when: Vet accepts to service request; terminates service; declines service request
    # Vet gets notified when: Farmer registers new livestock ???
    # Farmer gets notified when: Farmer registers new livestock, livestock health status is 'dead' or 'sick'
    # Farmer gets notified when: Vet adds a note on livestock health record
    # Vet and Farmer get notified when: Sensor observes an abnormality in livestock reading
    # Farmer also gets notified when: Sensor experience a breakdown or battery is going down

    @classmethod
    def notify_vet_vetcare(cls, session, created=False):
        # Vet gets notified when: Farmer requests service; terminates service
        farmer_name = session.farmer.user.get_fullname()
        vet_name = session.vet.user.get_fullname()

        if created and session.status == SessionStatus.PENDING:
            message = f"You have a service request from {farmer_name} for livestock support."

        elif session.status == SessionStatus.CONCLUDED:
            message = f"{farmer_name} has concluded the livestock support service."

    @classmethod
    def notify_farmer_vetcare(cls, session, created=False):
        # Farmer gets notified when: Vet accepts to service request; terminates service; declines service request
        farmer_name = session.farmer.user.get_fullname()
        vet_name = session.vet.user.get_fullname()

        if session.status == SessionStatus.ACCEPTED:
            message = f"Your request for livestock support has been accepted by {vet_name}."

        elif session.status == SessionStatus.DECLINED:
            message = f"{vet_name} isn't available right now. You can resubmit your request or pick another available vet to continue."

        elif session.status == SessionStatus.CONCLUDED:
            message = f"{vet_name} has concluded the livestock support service."

    @classmethod
    def notify_vet_livestock(cls, livestock, created=False):
        # Vet gets notified when: Farmer registers new livestock, livestock health status is 'dead' or 'sick' ???
        farmer_name = livestock.owner.user.get_fullname()
        livestock_name = livestock.get_fullname()

        if created:
            template = TEMPLATES["vet_livestock_registered"]
            message = template.format(farmer_name=farmer_name, livestock_name=livestock_name, timestamp=cls.TIMESTAMP)
        elif livestock.health_status == HealthStatus.SICK:
            template = TEMPLATES["vet_livestock_sick"]
            message = template.format(farmer_name=farmer_name, livestock_name=livestock_name, timestamp=cls.TIMESTAMP)
        elif livestock.health_status == HealthStatus.DECEASED:
            template = TEMPLATES["vet_livestock_deceased"]
            message = template.format(farmer_name=farmer_name, livestock_name=livestock_name, timestamp=cls.TIMESTAMP)

    @classmethod
    def notify_farmer_livestock(cls, livestock, created=False):
        # Farmer gets notified when: Farmer registers new livestock, livestock health status is 'dead' or 'sick'
        farmer_name = livestock.owner.user.get_fullname()
        livestock_name = livestock.get_fullname()
        device_id = livestock.sensor_device.device_id

        if created:
            template = TEMPLATES["farmer_livestock_registered"]
            message = template.format(farmer_name=farmer_name, livestock_name=livestock_name, timestamp=cls.TIMESTAMP, device_id=device_id)
        elif livestock.health_status == HealthStatus.SICK:
            template = TEMPLATES["farmer_livestock_sick"]
            message = template.format(farmer_name=farmer_name, livestock_name=livestock_name, timestamp=cls.TIMESTAMP)
        elif livestock.health_status == HealthStatus.DEAD:
            template = TEMPLATES["farmer_livestock_deceased"]
            message = template.format(farmer_name=farmer_name, livestock_name=livestock_name, timestamp=cls.TIMESTAMP)

    @classmethod
    def notify_vet_sensor(cls):
        # Vet gets notified when: Sensor observes an abnormality in livestock reading
        pass

    @classmethod
    def notify_farmer_sensor(cls):
        # Farmer gets notified when: Sensor observes an abnormality in livestock reading, experiences a breakdown or battery low
        pass

    @classmethod
    def notify_farmer_record(cls):
        # Farmer gets notified when: Vet adds a note on livestock health record
        pass


TEMPLATES = {
    "farmer_livestock_registered": "Your livestock '{livestock_name}' with tracker id '{device_id}' was successfully registered on {timestamp}.",
    "farmer_livestock_sick": "{livestock_name} was marked as sick on {timestamp}. Consider scheduling a vet check-up soon.",
    "farmer_livestock_deceased": "We're sorry - your livestock '{livestock_name}' was recorded as deceased on {timestamp}. Please review your records.",
    "vet_livestock_registered": "The livestock '{livestock_name}' was registered by {farmer_name} on {timestamp}.",
    "vet_livestock_sick": "The livestock '{livestock_name}' from {farmer_name} has been reported as sick on {timestamp}. You may want to follow up or prepare for a possible session.",
    "vet_livestock_deceased": "The livestock '{livestock_name}' belonging to {farmer_name} was recorded as deceased on {timestamp}. No further support is needed for this animal.",
}
