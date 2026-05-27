from django.conf import settings
from django.db import models
from django.utils import timezone

class Assistant(models.Model):
    class Meta:
        unique_together = (('ID','date'))
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    event_type = models.IntegerField()
    role = models.IntegerField()
    event_name = models.CharField(max_length=256)
    theme = models.CharField(max_length=256)
    date = models.DateField()
    event_addr = models.CharField(max_length=80)
    hash = models.CharField(max_length=64)

