from django.db import models

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    content = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

class ScannedAWB(models.Model):
    awb_number = models.CharField(max_length=100)
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    
