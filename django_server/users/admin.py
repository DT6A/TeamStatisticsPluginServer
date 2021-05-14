from django.contrib import admin
from .models import UserStat, Profile, UserUniqueToken

admin.site.register(UserStat)
admin.site.register(Profile)
admin.site.register(UserUniqueToken)
