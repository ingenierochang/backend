from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class Restaurant(models.Model):
    # Basic
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    # Media
    logo_image = models.ImageField(null=True, blank=True)

    # Information
    slogan = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=1000, blank=True, null=True)
    address_url = models.CharField(max_length=5000, blank=True, null=True)

    # Contact
    whatsapp = models.BigIntegerField(blank=True, null=True)
    facebook = models.CharField(max_length=1000, blank=True, null=True)
    instagram = models.CharField(max_length=1000, blank=True, null=True)
    tiktok = models.CharField(max_length=1000, blank=True, null=True)
    phone = models.BigIntegerField(blank=True, null=True)

    # Other Info
    open_hours = models.TextField(blank=True, null=True)
    payment_methods = models.TextField(blank=True, null=True)
    parking = models.CharField(max_length=2000, blank=True, null=True)
    alcohol_patents = models.CharField(max_length=2000, blank=True, null=True)
    website = models.CharField(max_length=2000, blank=True, null=True)

    # Extensions
    whatsapp_orders_extension = models.BooleanField(default=False)
    category_clusters_extension = models.BooleanField(default=False)
    price_options_extension = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)

        if self.logo_image:
            # Open the image
            img = Image.open(self.logo_image)

            # Resize the image to exact dimensions (100x100)
            desired_width = 150
            desired_height = 150
            img = img.resize((desired_width, desired_height), Image.BICUBIC)

            # Convert the image to WebP format
            img_io = BytesIO()
            img.save(img_io, format='WEBP', quality=96)

            # Update the image field with the compressed WebP image
            self.logo_image.save(f"{self.slug}_logo.webp", ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
