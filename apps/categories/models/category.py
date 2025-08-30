from django.db import models
from django.utils.text import slugify
from apps.restaurants.models.restaurant import Restaurant


# Create your models here.

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    image = models.CharField(max_length=5000, null=True, blank=True)

    order = models.PositiveIntegerField(default=99999, help_text="Order of the category cluster for sorting.")


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name