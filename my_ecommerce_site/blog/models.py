from django.urls import reverse
from django.utils.text import slugify
from django.db import models
from django.db import models
from tinymce.models import HTMLField

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = HTMLField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_details', args=[self.slug])

    def __str__(self):
        return self.title

