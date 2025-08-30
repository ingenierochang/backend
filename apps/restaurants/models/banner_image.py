from django.db import models
from apps.restaurants.models.restaurant import Restaurant
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class BannerImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, related_name='banner_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banner_images/')

    def save(self, *args, **kwargs):
        if self.image:
            # Open the image
            img = Image.open(self.image)

            # Resize the image to the exact desired dimensions
            desired_width = int(300 * 1.6)
            desired_height = int(100 * 1.6)
            img = img.resize((desired_width, desired_height), resample=Image.BICUBIC)

            # Convert the image to WebP format
            img_io = BytesIO()
            img.save(img_io, format='WEBP', quality=97)

            # Update the image field with the resized WebP image
            self.image.save(f"{self.restaurant.slug}_banner.webp", ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)
