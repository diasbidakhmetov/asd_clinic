from django.contrib import admin

# Register your models here.

from users.models import Gender, User, UserRole

admin.site.register(Gender)
admin.site.register(User)
admin.site.register(UserRole)