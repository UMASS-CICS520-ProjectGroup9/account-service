from django.db import models

# Create your models here.
class Account(models.Model):
    accountID = models.AutoField(primary_key=True)
    creator_id = models.IntegerField(null=True, blank=True) # user ID comes from token
    email = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)
    fullname = models.CharField(max_length=1500)
    role = models.CharField(max_length=50, default="STUDENT")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   

    def __repr__(self):
        return  f"Account(email={self.email}, fullname={self.fullname}, role={self.role}, is_active={self.is_active})"
    
    
