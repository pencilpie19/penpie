#Coding by Muhammet Bulut - CEO of Pencil Pie
from django.contrib import admin
from .models import UserProfile,UserBlocking,ProfileRiver,Photo,Notifications,CoverPhoto,UserLog
# Register your models here.
@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user","gender","birth_date"]
    class Meta:
        model=UserProfile

@admin.register(UserBlocking)
class BlockingAdmin(admin.ModelAdmin):
    list_display = ["blocker","blocked"]
    class Meta:
        model=UserBlocking

@admin.register(Notifications)
class NotifyAdmin(admin.ModelAdmin):
    list_display = ["is_unread","user","content_type","object_id"]
    class Meta:
        model=Notifications

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ["user","file"]
    class Meta:
        model=Photo


@admin.register(CoverPhoto)
class CoverAdmin(admin.ModelAdmin):
    list_display = ["user","file"]
    class Meta:
        model=CoverPhoto

@admin.register(ProfileRiver)
class RiverAdmin(admin.ModelAdmin):
    list_display = ["object_id","user","content_type"]
    class Meta:
        model=ProfileRiver

@admin.register(UserLog)
class LogAdmin(admin.ModelAdmin):
    list_display = ["is_active","object_id","user","content_type","ip_adress"]
    class Meta:
        model=UserLog