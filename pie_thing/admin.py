#Coding by Muhammet Bulut - CEO of Pencil Pie
from django.contrib import admin
from .models import Thing,Comment,SupportComment,Report,Repost,SameThing,ThingReport,Help
#

admin.site.site_header="PencilPie Yönetimi"
@admin.register(Thing)
class ThingAdmin(admin.ModelAdmin):

    list_display = ["title","author","created_date"]

    list_display_links = ["title","created_date"]

    search_fields = ["title"]

    list_filter = ["created_date"]
    class Meta:
        model = Thing

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id","user","content_object","content","opt","point"]
    list_filter = ["created_date"]
    class Meta:
        model=Comment

@admin.register(SupportComment)
class SupAdmin(admin.ModelAdmin):
    list_display = ["user","comment","sup_type","id"]
    class Meta:
        model=SupportComment

@admin.register(Help)
class HelpAdmin(admin.ModelAdmin):
    list_display = ["user","help_date","help_content"]
    class Meta:
        model=Help

@admin.register(Report)
class RepAdmin(admin.ModelAdmin):
    list_display = ["user","comment","report_date"]
    list_filter = ["report_date"]
    class Meta:
        model=Report

@admin.register(Repost)
class RepostAdmin(admin.ModelAdmin):
    list_display = ["user","reposting_comment","repost_date","id"]
    list_filter = ["repost_date"]
    class Meta:
        model=Repost

@admin.register(SameThing)
class SameAdmin(admin.ModelAdmin):
    list_display = ["user","thing","report_date","id"]
    list_filter = ["report_date"]
    class Meta:
        model=SameThing


@admin.register(ThingReport)
class ThingRepAdmin(admin.ModelAdmin):
    list_display = ["user","thing","report_date","id"]
    list_filter = ["report_date"]
    class Meta:
        model=ThingReport