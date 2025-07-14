from django.db import models
from django.conf import settings
from tours.models import Tour

class MediaFile(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='media_files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='media_files/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} by {self.uploaded_by.username}"