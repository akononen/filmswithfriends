from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.

class Text(models.Model):
    input = models.TextField(blank=False, null=False, max_length=255, default='')

    def __str__(self):
        return self.input
