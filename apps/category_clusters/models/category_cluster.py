from django.db import models
from django.utils.text import slugify
from apps.restaurants.models.restaurant import Restaurant
from apps.categories.models.category import Category
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class CategoryCluster(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    image = models.ImageField(upload_to='category_cluster_images/', blank=True, null=True, help_text="Small image used for product previews.")

    categories = models.ManyToManyField(Category, related_name='category_clusters')

    order = models.PositiveIntegerField(default=99999, help_text="Order of the category cluster for sorting.")

    def save(self, *args, **kwargs):

        if not self.slug or self.slug != slugify(self.name):
            self.slug = slugify(self.name)

        if self.image:
            # Open the image
            img = Image.open(self.image)

            # Calculate the crop box to maintain aspect ratio
            width, height = img.size
            target_width, target_height = 400, 150
            aspect_ratio = target_width / target_height

            if width / height > aspect_ratio:
                # Image is wider than target aspect ratio
                new_width = int(height * aspect_ratio)
                left = (width - new_width) / 2
                top = 0
                right = left + new_width
                bottom = height
            else:
                # Image is taller or equal to target aspect ratio
                new_height = int(width / aspect_ratio)
                left = 0
                top = (height - new_height) / 2
                right = width
                bottom = top + new_height

            # Crop the image to the target aspect ratio
            img = img.crop((left, top, right, bottom))

            # Resize the image to exact dimensions (400x150)
            img = img.resize((target_width, target_height), Image.BICUBIC)

            # Convert the image to WebP format
            img_io = BytesIO()
            img.save(img_io, format='WEBP', quality=80)

            # Update the image field with the compressed WebP image
            self.image.save(f"{self.restaurant.slug}_banner.webp", ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
