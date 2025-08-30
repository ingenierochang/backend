from django.db import models
from apps.restaurants.models.restaurant import Restaurant
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    image = models.CharField(max_length=5000, null=True, blank=True) 

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name