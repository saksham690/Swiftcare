from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField()  # External image URL
    description = models.TextField()
