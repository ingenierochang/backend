from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Profile(models.Model):

	"""
	This model acts as a way to put custom
	attributes in User model.

	We need an attribute of limit of menus a User can build
	so we can retrieve the information like this:

	user.profile.menus_limit (user.custom_model.attribute)
	"""

	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200)

	def __str__(self):

		return self.name