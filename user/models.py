# Coding by Muhammet Bulut - CEO of Pencil Pie
from django.contrib.admin import ModelAdmin
from django.db import models
from following.models import Following
from django.contrib.auth.models import User
from django.shortcuts import reverse,get_object_or_404
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
import os
from datetime import date
from django.contrib.auth.admin import UserAdmin

UserAdmin.list_display += ('date_joined',)

def get_file_path_for_user(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('userprofilephoto/{}'.format(date.today()), filename)

def get_file_path_for_user_cover(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('usercoverphoto/{}'.format(date.today()), filename)

class Photo(models.Model):
    user=models.ForeignKey(User,related_name="profilephoto",on_delete=models.CASCADE)
    file = models.ImageField(default="default/default.png",upload_to=get_file_path_for_user)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def get_pp(self):
        print(self.file.path,"selam")
        return self.file.path

    class Meta:
        verbose_name = 'photo'
        verbose_name_plural = 'photos'

class CoverPhoto(models.Model):
    user=models.ForeignKey(User,related_name="coverphoto",on_delete=models.CASCADE)
    file = models.ImageField(default="default/cover.jpg",upload_to=get_file_path_for_user_cover)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def get_cp(self):
        return self.file.path

    class Meta:
        verbose_name = 'coverphoto'
        verbose_name_plural = 'coverphotos'

class UserProfile(models.Model):
    GENDER = ((None, "Cinsiyet"), ('erkek', 'Erkek'), ('kadın', 'Kadın'), ('diger', 'Diğer'))
    user = models.OneToOneField(User, null=True, blank=False, verbose_name="User", on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, verbose_name='Hakkımda', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name='Doğum Tarihi')
    gender = models.CharField(choices=GENDER, blank=False, null=True, max_length=10, verbose_name='Cinsiyet')

    class Meta:
        verbose_name_plural = "Profiller"

    def get_profile_river(self):
        return self.user.profileriver.all().order_by("-river_date")

    def get_noti_count(self):
        count=Notifications.objects.filter(user=self.user,is_unread=True).count()
        return count
    def get_followed_list(self):

        followed = Following.get_followeds(self.user)

        return followed.values_list('followed__username',flat=True)

    def get_follower_count(self):
        foll_count = Following.get_fol_count(self.user)
        follower_count = foll_count["followers"]
        return follower_count

    def get_followed_count(self):
        foll_count = Following.get_fol_count(self.user)
        followed_count = foll_count["followeds"]
        return followed_count

    def get_screen_name(self):
        user = self.user
        if user.get_full_name():
            return user.get_full_name()
        return user.username

    def user_full_name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        return None
    def get_anything(self,user):
        return True
    def get_user_url(self):
        url = reverse('user:profile', kwargs={'username': self.user.username})
        return url

    def get_profile_photo(self):
        try:
            go = Photo.objects.get(user=self.user)
            return go.file.url
        except Photo.DoesNotExist:
            return "/media/default/profile.jpg"
    def get_cover_photo(self):
        try:
            go = CoverPhoto.objects.get(user=self.user)
            return go.file.url
        except CoverPhoto.DoesNotExist:
            return "/media/default/cover.jpg"

    def __str__(self):
        return "%s Profile" % (self.get_screen_name())

class UserBlocking(models.Model):
    blocker = models.ForeignKey(User, related_name="blocker", null=True, verbose_name="Blocker", on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name="blocked", null=True, verbose_name="Blocked", on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural="Engellemeler"

class ProfileRiver(models.Model):
    user = models.ForeignKey(User, null=True, related_name="profileriver", on_delete=models.CASCADE)
    content_type = models.ForeignKey(to=ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    river_date=models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        verbose_name_plural = "Profil Akışları"

    @classmethod
    def add_river(cls, obj, user):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        cls.objects.create(user=user, content_type=content_type, object_id=obj.id)

    @classmethod
    def delete_river(cls, obj, user):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        cls.objects.filter(user=user, content_type=content_type, object_id=obj.id).delete()


    def tell_me_what_is_this(self):
        if self.content_type.__str__()=="comment":
            return True
        else:
            return False

class Notifications(models.Model):
    user = models.ForeignKey(User, related_name="notifications", null=True, verbose_name="Kullanıcı", on_delete=models.CASCADE)
    content_type=models.ForeignKey(to=ContentType,null=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_unread=models.BooleanField(default=True)
    notification_date=models.DateTimeField(auto_now_add=True,null=True)




    def tell_me_what_is_this(self):
        if self.content_type.__str__() =="support comment":
            return 1
        elif self.content_type.__str__() =="comment":
            return 2
        elif self.content_type.__str__() =="following":
            return 3
        elif self.content_type.__str__() =="repost":
            return 4

    @classmethod
    def add_notification(cls,user,obj,request):
        if user!=request.user:
            content_type=ContentType.objects.get_for_model(obj.__class__)
            cls.objects.create(user=user,content_type=content_type,object_id=obj.id)
        else:
            pass
    @classmethod
    def delete_notification(cls,obj,request):
        if obj!=None:
            content_type=ContentType.objects.get_for_model(obj.__class__)
            cls.objects.filter(content_type=content_type,object_id=obj.id).delete()
        else:
            pass

    class Meta:
        verbose_name_plural="Bildirimler"

class UserLog(models.Model):
    user = models.ForeignKey(User, null=True, related_name="logs", on_delete=models.CASCADE)
    content_type = models.ForeignKey(to=ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    activity_date = models.DateTimeField(auto_now_add=True, null=True)
    ip_adress=models.CharField(max_length=50,blank=True,null=True)
    is_active=models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = "Hareketler"

    @classmethod
    def add_log(cls, obj, user,ip_adress):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        cls.objects.create(user=user, content_type=content_type, object_id=obj.id,ip_adress=ip_adress)

    @classmethod
    def delete_log(cls, obj,user):
        if obj != None:
            content_type = ContentType.objects.get_for_model(obj.__class__)
            log=cls.objects.get(content_type=content_type, object_id=obj.id,user=user)
            log.is_active=False
            log.save()
        else:
            pass

    def tell_me_what_is_this(self):
        if self.content_type.__str__() =="support comment":
            return 1
        elif self.content_type.__str__() =="comment":
            return 2
        elif self.content_type.__str__() =="thing":
            return 3
        elif self.content_type.__str__() =="repost":
            return 4