from django.db import models

# Create your models here.

class FileUpload(models.Model):
    # file = models.FileField(null=True)
    file = models.FileField(null=True, upload_to='files/')
    original_filename = models.CharField(max_length=255, blank=True, null=True)