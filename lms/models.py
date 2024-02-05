import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from actions.models import MediaAction
from files.models import Media
from users.models import User


GENDER_CHOICES = (
    ("f", _("female")),
    ("m", _("male")),
    ("o", _("other")),
)


class Customer(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    business_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    business_management_number = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    learners = models.ManyToManyField("Learner", blank=True, related_name="customers")


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    year_of_birth = models.CharField(max_length=10, null=True, blank=True)
    birthday = models.CharField(max_length=10, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_CHOICES)
    cellphone = models.CharField(max_length=50, null=True, blank=True)

    department = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    job_responsibility = models.CharField(max_length=100, null=True, blank=True)
    occupation_type = models.CharField(max_length=10, null=True, blank=True)
    working_type = models.CharField(max_length=10, null=True, blank=True)
