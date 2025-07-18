from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

# Create your models here.
 
 #Auitquery model
class AuditQuery(models.Model):
    QUERY_CHOICES = [
        ('Discussion', 'Discussion'),
        ('Accounting', 'Accounting'),
        ('Conceptual', 'Conceptual'),
    ]

    STATUS_CHOICES = [
        ('Done', 'Done'),
        ('Pending', 'Pending'),
        ('Discussion Point', 'Discussion Point'),
    ]

    query_type = models.CharField(max_length=20, choices=QUERY_CHOICES,default='Enter status')
    auditee_action_owner = models.CharField(max_length=255)
    auditee_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Enter status')
    auditor_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Enter status')
    remarks = models.TextField(blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    updated_time = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()

    def __str__(self):
        return f"Query #{self.id} - {self.query_type}"

#profile model
class Profile(models.Model):
    ROLE_CHOICES = [
        ('Auditor', 'Auditor'),
        ('Auditee', 'Auditee'),
        # ('SuperAdmin','superAdmin'),

    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True,null=True)  
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    # audit_query_Log/models.py



def save_model(self, request, obj, form, change):
    obj._updated_by = request.user  # pass user to signal
    super().save_model(request, obj, form, change)
 