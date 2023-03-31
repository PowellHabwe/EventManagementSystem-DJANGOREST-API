from django.db import models

# Create your models here.
class Ticket(models.Model):
    code = models.CharField(default="", max_length=8, unique=True)
    title = models.CharField(max_length=50)
    price = models.PositiveIntegerField(default = 0)