#Coding by Muhammet Bulut - CEO of Pencil Pie
import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Avg, Sum
from django.shortcuts import reverse,get_object_or_404
from django.template.defaultfilters import slugify
from unidecode import unidecode
from user.models import User,ProfileRiver,Notifications,UserLog
import uuid
import os
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your models here.
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('thingimage', filename)

def get_file_path_for_user(instance, filename,username):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('userprofilephoto/{}'.format(username), filename)


class Thing(models.Model):
    title = models.CharField( max_length=30,blank=False,null=True,verbose_name="Tartışma Başlığı",help_text="Lütfen tartışma başlığını girin")
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE, verbose_name="Yazar")
    opt1 = models.CharField(max_length=12,blank=False,null=False,verbose_name="İlk seçenek")
    opt2 = models.CharField(max_length=12,blank=False,null=False, verbose_name="İkinci seçenek")
    opt3=models.CharField(default="Tarafsız",verbose_name="İkinci Seçenek",max_length=50)
    content = models.TextField(verbose_name="Açıklama")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    thingimage=models.FileField(default="default/defaultpost.jpg",upload_to=get_file_path,blank=True,null=True,verbose_name="Görsel Seçimi")
    slug=models.SlugField(null=True,unique=True,editable=True)

    def __str__(self):
        return self.title
    def save(self, *args,**kwargs):
        if self.id is None:
            title=self.title
            self.slug=slugify(unidecode(title))
        super(Thing, self).save(*args,**kwargs)
    #Fonksiyon kullanıldığında direkt olarak objenin url'sini veriri.
    def get_absolute_url(self):
        return reverse('pie_thing:thing',kwargs={'slug':self.slug})
    class Meta:
        verbose_name_plural="Tartışmalar"
        ordering = ['-created_date']
    def get_thing_comment(self):
        content_type=ContentType.objects.get_for_model(self)
        object_id=self.id
        all_comment=Comment.objects.filter(content_type=content_type,object_id=object_id).order_by('-created_date')
        return all_comment
    def get_percent(self):
        count=self.get_comment_count()
        if count !=0:
            content_type = ContentType.objects.get_for_model(self)
            object_id = self.id


            point1=Comment.objects.filter(content_type=content_type,object_id=object_id,opt=1).aggregate(Sum("point"))["point__sum"]

            if point1==None or point1<0:
                point1=0

            point2=Comment.objects.filter(content_type=content_type,object_id=object_id,opt=2).aggregate(Sum("point"))["point__sum"]
            if point2==None or point2<0:
                point2=0

            point3=Comment.objects.filter(content_type=content_type,object_id=object_id,opt=3).aggregate(Sum("point"))["point__sum"]
            if point3==None or point3<0:
                point3=0


            count=point3+point2+point1+count
            opt1=Comment.objects.filter(content_type=content_type,object_id=object_id,opt=1).count()+point1
            opt2=Comment.objects.filter(content_type=content_type,object_id=object_id,opt=2).count()+point2
            opt3=Comment.objects.filter(content_type=content_type,object_id=object_id,opt=3).count()+point3

            return {1:int(opt1/count*100),2:int(opt2/count*100),3:int(opt3/count*100)}
        else:
            return "zero"
    def get_comment_count(self):
        content_type = ContentType.objects.get_for_model(self)
        object_id = self.id
        all_comment = Comment.objects.filter(content_type=content_type, object_id=object_id).order_by('-created_date').count()
        return all_comment

class Comment(models.Model):
    user=models.ForeignKey(User,null=True,default=1,related_name="comments",on_delete=models.CASCADE)
    is_parent=models.BooleanField(default=False)
    opt=models.PositiveIntegerField(default=1)
    content_type=models.ForeignKey(to=ContentType,null=True,on_delete=models.CASCADE)
    object_id=models.PositiveIntegerField()
    content_object=GenericForeignKey('content_type','object_id')
    content=models.TextField(verbose_name='Yorum',blank=False,null=True)
    created_date=models.DateTimeField(auto_now_add=True, null=True)
    photo = models.ImageField(upload_to="comment",blank=True,null=True)
    is_repost=models.BooleanField(default=False)
    is_anon=models.BooleanField(default=False)
    point=models.IntegerField(default=0)
    def __str__(self):
        username=self.user.username
        text="{0} {1}".format(username,self.content_type.model)
        return text
    class Meta:
        verbose_name_plural="Yorumlar"

    @classmethod
    def compressImage(cls, uploadedImage):
        imageTemproary = Image.open(uploadedImage)
        if imageTemproary.mode in ("RGBA", "P"):
            imageTemproary = imageTemproary.convert("RGB")
        outputIoStream = BytesIO()
        width, height = imageTemproary.size
        imageTemproaryResized = imageTemproary.resize((int(width/1.2), int(height/1.2)))
        imageTemproaryResized.save(outputIoStream, format='JPEG', quality=80)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0],
                                             'image/jpeg', sys.getsizeof(outputIoStream), None)
        return uploadedImage


    @classmethod
    def add_comment(cls,obj,model_type,user,content,options,photo,ip,request,is_anon):
        if photo:
            photo=cls.compressImage(photo)
        content_type=ContentType.objects.get_for_model(obj.__class__)
        comment=cls.objects.create(user=user,is_anon=is_anon,content=content,content_type=content_type,object_id=obj.id,opt=options,photo=photo)
        ProfileRiver.add_river(comment,user)
        UserLog.add_log(obj=comment,user=comment.user,ip_adress=ip)
        if model_type=="comment":
            Notifications.add_notification(obj.user,comment,request=request)
            obj.is_parent=True
            obj.save()
    def get_child_comment(self):
        if self.is_parent:
            content_type=ContentType.objects.get_for_model(self.__class__)
            all_child_comment=Comment.objects.filter(content_type=content_type,object_id=self.id).order_by('-created_date')
            return all_child_comment
        return None
    def get_child_comment_count(self):
        if self.is_parent:
            content_type=ContentType.objects.get_for_model(self.__class__)
            all_child_comment=Comment.objects.filter(content_type=content_type,object_id=self.id).order_by('-created_date').count()
            return all_child_comment
        return 0

    def get_sup_count(self):
        sup_count=self.sups.filter(sup_type=1).count()
        return sup_count
    def get_un_sup_count(self):
        sup_count=self.sups.filter(sup_type=0).count()
        return sup_count

    def get_sup_comment_user(self):
        return self.sups.filter(sup_type=1).values_list('user__username', flat=True)
    def get_un_sup_comment_user(self):
        return self.sups.filter(sup_type=0).values_list("user__username",flat=True)
    def get_sup_user_as_object(self):
        data_list = []
        qs = self.sups.all()
        for obj in qs:
            data_list.append(obj.user)
        return data_list
    def is_father(self):

        if self.content_type.model=="comment":
            return False
        elif self.content_type.model=="thing":
            return True
    def get_repost_count(self):
        rep_count=self.reposts.count()
        return rep_count

class SupportComment(models.Model):
    comment=models.ForeignKey(Comment,on_delete=models.CASCADE,verbose_name="Destek",related_name="sups")
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,verbose_name="Kullanıcı",related_name="sups")
    sup_type=models.PositiveIntegerField(null=False,default=1)

    class Meta:
        verbose_name_plural="Desteklenen Yorumlar"

    def __str__(self):
        return "%s %s" % (self.user,self.comment)

class Report(models.Model):
    user=models.ForeignKey(User,null=True,related_name="reports",on_delete=models.CASCADE)
    comment=models.ForeignKey(Comment,null=True,related_name="reports",on_delete=models.CASCADE)
    report_date = models.DateTimeField(auto_now_add=True)
    report_content=models.TextField(max_length=1000,blank=False,null=True,verbose_name="Sana daha iyi bir hizmet sunabilmemiz için içeriği bildirmendeki sebebi bize kısaca açıkla..")

    class Meta:
        verbose_name_plural="Şikayetler"

    def __str__(self):
        return "%s %s" % (self.user,self.report_content)

class SameThing(models.Model):
    user=models.ForeignKey(User,null=True,related_name="samething",on_delete=models.CASCADE)
    thing=models.ForeignKey(Thing,null=True,related_name="samething",on_delete=models.CASCADE)
    report_date=models.DateTimeField(auto_now_add=True)
    content=models.CharField(max_length=1000,blank=False,null=True,verbose_name="Benzediğini düşündüğün tartışmanın başlığını veya url'ini yaz.")

    class Meta:
        verbose_name_plural="'Aynı Tartışma' Şikayeti"



class ThingReport(models.Model):
    user=models.ForeignKey(User,null=True,related_name="thingreports",on_delete=models.CASCADE)
    thing=models.ForeignKey(Thing,null=True,related_name="reports",on_delete=models.CASCADE)
    report_date=models.DateTimeField(auto_now_add=True)
    content=models.CharField(max_length=1000,blank=False,null=True,verbose_name="Sana daha iyi bir hizmet sunabilmemiz için içeriği bildirmendeki sebebi bize kısaca açıkla..")

    class Meta:
        verbose_name_plural="Tartışma Şikayeti"

class Repost(models.Model):
    user = models.ForeignKey(User, null=True, default=1, related_name="reposts", on_delete=models.CASCADE)
    repost_content=models.CharField(max_length=200,blank=True,null=True,verbose_name="Dipnot")
    reposting_comment=models.ForeignKey(Comment,on_delete=models.CASCADE,related_name="reposts")
    repost_date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="Alıntılar"


class Help(models.Model):
    user=models.ForeignKey(User,null=True,related_name="helps",on_delete=models.CASCADE)
    help_content=models.TextField(max_length=3000,blank=False,null=False,verbose_name="Seni dinliyoruz")
    help_date=models.DateTimeField(auto_now_add=True)
