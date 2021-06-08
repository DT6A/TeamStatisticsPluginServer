from django.contrib import admin
from .models import *

admin.site.register(UserStat)
admin.site.register(Profile)
admin.site.register(UserUniqueToken)
admin.site.register(Team)
admin.site.register(CharCountingMetric)
admin.site.register(SubstringCountingMetric)
admin.site.register(Achievement)
admin.site.register(FeedMessage)
