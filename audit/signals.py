from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import AuditQuery
from django.contrib.auth.models import User
import threading

# Thread-local storage to store the current user
_thread_locals = threading.local()

def set_current_user(user):
    _thread_locals.user = user

def get_current_user():
    return getattr(_thread_locals, 'user', None)






