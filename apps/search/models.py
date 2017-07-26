from __future__ import unicode_literals

from django.db import models

class Credential(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    grant_type = models.CharField(max_length=255)
