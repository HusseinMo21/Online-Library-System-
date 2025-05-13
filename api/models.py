from django.db import models
from django.utils.text import slugify
from users.models import User
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100, null=False, blank=False)
    release_year = models.IntegerField(null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    author = models.CharField(max_length=100, null=False, blank=False, default='')
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='books'
    )
    is_read = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        import datetime

        if self.release_year > datetime.datetime.now().year:
            raise ValidationError({'release_year': "Release year cannot be in the future."})

        if self.price < 0:
            raise ValidationError({'price': "Price must be a positive value."})

    def save(self, *args, **kwargs):
        self.full_clean()  # This will call clean() method and raise ValidationError if any
        super().save(*args, **kwargs)


