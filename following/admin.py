#Coding by Muhammet Bulut - CEO of Pencil Pie

from django.contrib import admin
from .models import Following
# Register your models here.
@admin.register(Following)
class FollowAdmin(admin.ModelAdmin):
    list_display = ["follower","followed"]
    class Meta:
        model=Following