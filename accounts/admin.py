from django.contrib import admin
from accounts.models import UserAccount
from . import models

# Register your models here.


admin.site.register(UserAccount)
