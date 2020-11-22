import uuid
import os
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

# recommended way to retrieve different settings from the
# Django settings file so "settings" retrieve auth user model
from django.conf import settings
from django.db.models.deletion import CASCADE


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('upload/recipe/', filename)


class UserManager(BaseUserManager):
    # **extra_fields (optional) => take any of the extra functions
    # that are passed in
    # when call the create_user and pass them into extra fields then
    # add any additinal filds that we create without user model
    def create_user(self, email, password=None, **extra_fields):
        """Create and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        # normalize_email => help function that comes with the BaseUserManager
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # password is encrypted is not stored in clear text
        # so use set_password functions
        user.set_password(password)
        # required for supporting mutiple database
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        # use command-line so don't need to worry about **extra_fields
        """Create and saves a new super user"""
        # create superuser using create_user function
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        # because we modified the user we need to save it
        user.save(using=self._db)

        return user


# this does is it basically gives us all the features that
# come out of the box
# with the Django user model but we can then build on top
# of them and customize
# it to support our email address
class User(AbstractBaseUser, PermissionsMixin):
    """Custiom user model that suppors using email instead od username"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    # determine if the user in the system is active or not
    # it allows us to deactive users that we require
    is_active = models.BooleanField(default=True)
    # if want to create staff user gonna have to use a special commend
    is_staff = models.BooleanField(default=False)

    # create UserManager object
    objects = UserManager()

    # default the USERNAME_FIELD is customizing that to email
    USERNAME_FIELD = "email"


class Tag(models.Model):
    """Tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    # best practice method of retrieving the AUTH_USER_MODEL
    # setting from Django settings
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Recipe object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title
