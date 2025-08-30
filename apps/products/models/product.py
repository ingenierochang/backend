from django.db import models
from apps.categories.models.category import Category
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from apps.restaurants.models.restaurant import Restaurant

class Product(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(blank=True, unique=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    discounted_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    # image = models.ImageField(upload_to='products/', null=True, blank=True)
    thumbnail_image = models.ImageField(upload_to='product_images/thumbnails/', blank=True, null=True, help_text="Small image used for product previews.")
    detail_image = models.ImageField(upload_to='product_images/detail/', blank=True, null=True, help_text="Large image used for detailed views.")

    updated_at = models.DateTimeField(auto_now=True)

    order = models.PositiveIntegerField(default=99999, help_text="Order of the category cluster for sorting.")


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            n = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['slug']),
        ]
