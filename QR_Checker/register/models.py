from django.db import models

class Post(models.Model):
    class Meta:
        unique_together = (('ID','date'))
    ID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    event_type = models.TextField()
    role = models.TextField()
    event_name = models.CharField(max_length=256)
    theme = models.CharField(max_length=256)
    date = models.DateField()
    event_addr = models.CharField(max_length=256)

    
