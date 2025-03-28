from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=100, unique=True)
    year = models.CharField(max_length=10)
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.year})"
