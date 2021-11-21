from django.contrib import admin

from .models import Group, Member, TimeTable, TimeBlock


# Register your models here.
admin.site.register(Group)
admin.site.register(Member)
admin.site.register(TimeTable)
admin.site.register(TimeBlock)
