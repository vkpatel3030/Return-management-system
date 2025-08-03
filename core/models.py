from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ScannedAWB(models.Model):
    awb_number = models.CharField(max_length=100)
    scanned_at = models.DateTimeField(auto_now_add=True)
    
    
