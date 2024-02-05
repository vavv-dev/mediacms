import json
import math
from numbers import Number

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from files.models import Media
from users.models import User

USER_MEDIA_ACTIONS = (
    ("like", "Like"),
    ("dislike", "Dislike"),
    ("watch", "Watch"),
    ("report", "Report"),
    ("rate", "Rate"),
)


class MediaAction(models.Model):
    """Stores different user actions"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        blank=True,
        null=True,
        related_name="useractions",
    )
    session_key = models.CharField(
        max_length=33,
        db_index=True,
        blank=True,
        null=True,
        help_text="for not logged in users",
    )

    action = models.CharField(max_length=20, choices=USER_MEDIA_ACTIONS, default="watch")
    # keeps extra info, eg on report action, why it is reported
    extra_info = models.TextField(blank=True, null=True)

    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name="mediaactions")
    action_date = models.DateTimeField(auto_now_add=True)
    remote_ip = models.CharField(max_length=40, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(MediaAction, self).save(*args, **kwargs)

    def __str__(self):
        return self.action

    @classmethod
    def watch_data(cls, extra_info):
        data = {"watched": [], "clipped": {}, "position": 0}
        if extra_info:
            try:
                if isinstance(extra_info, str):
                    data.update(json.loads(extra_info))
                if isinstance(extra_info, dict):
                    data.update(extra_info)
            except json.JSONDecodeError:
                pass
        return data

    class Meta:
        indexes = [
            models.Index(fields=["user", "action", "-action_date"]),
            models.Index(fields=["session_key", "action"]),
        ]


class WatchState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    completion = models.FloatField(default=0)
    clips = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = (("user", "media"),)


@receiver(post_save, sender=MediaAction)
def update_watch(sender, instance, created, **kwargs):
    if instance.action != "watch":
        return

    if not (instance.user and instance.extra_info):
        return

    data = MediaAction.watch_data(instance.extra_info)

    # completion
    completion = 0
    if instance.media.duration:
        # really watched seconds
        watched = len([s for s in data.get("watched", []) if s])
        completion = min(watched / math.floor(instance.media.duration), 100)

    # clipped
    clipped = ",".join(data.get("clipped", {}).keys())

    WatchState.objects.update_or_create(
        user=instance.user,
        media=instance.media,
        defaults={
            "completion": completion,
            "clips": clipped,
        },
    )
