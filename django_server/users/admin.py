from django.contrib import admin
from .models import *

admin.site.register(UserStat)
admin.site.register(Profile)
admin.site.register(UserUniqueToken)
admin.site.register(Team)
admin.site.register(CharCountingMetric)
admin.site.register(Metric)
admin.site.register(SubstringCountingMetric)
admin.site.register(WordCountingMetric)
admin.site.register(SpecificBranchCommitCounterMetric)
admin.site.register(SpecificLengthCopyCounterMetric)
admin.site.register(SpecificLengthPasteCounterMetric)
admin.site.register(Achievement)
admin.site.register(FeedMessage)
