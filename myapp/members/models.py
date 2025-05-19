from datetime import timezone
from django.db import models 

class Members(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10)
    password = models.CharField(max_length=100, default="")
    
    def __str__(self):
        return self.name

class Attendance(models.Model):
    serialno = models.IntegerField(default=0)
    id = models.AutoField(primary_key=True)
    adate = models.DateField()
    atime = models.CharField(max_length=20, default='00:00:00')
    name = models.CharField(max_length=100, default='') 

    def __str__(self):
        return f"{self.name} - {self.adate} - {self.atime}"