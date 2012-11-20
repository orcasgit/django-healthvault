from django.contrib.auth.models import User
from django.db import models


class HealthVaultUser(models.Model):
    """
    Associates a Django user with a HealthVault data record.

    The association between a Django user and HealthVault record is
    one-to-one. The user can change the record they associate with at any
    time, but a single HealthVault record can only be associated with one
    Django user at a given time.
    """
    user = models.OneToOneField(User)

    # HealthVault UUID.
    record_id = models.CharField(max_length=36, unique=True)

    # Used to authorize the current session with HealthVault.
    token = models.TextField()

    def __unicode__(self):
        return self.user.__unicode__()
