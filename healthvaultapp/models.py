from django.contrib.auth.models import User
from django.db import models


class HealthVaultUser(models.Model):
    user = models.OneToOneField(User)
    token = models.TextField()

    def __unicode__(self):
        return self.user.__unicode__()
