from django.db import models

class Post(models.Model):
    class Meta:
        unique_together = (('ID','date'))
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=12)
    role = models.CharField(max_length=10)
    event_name = models.CharField(max_length=256)
    theme = models.CharField(max_length=256)
    date = models.DateField()
    event_addr = models.CharField(max_length=256)

    
