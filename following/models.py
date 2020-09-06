from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Following(models.Model):
    follower=models.ForeignKey(User,related_name="follower",null=True,verbose_name="Follower",on_delete=models.CASCADE)
    followed=models.ForeignKey(User,related_name="followed",null=True,verbose_name="Followed",on_delete=models.CASCADE)

    def __str__(self):
        return "Follower {} - Followed {}".format(self.follower,self.followed)
    @classmethod
    def follow_user(cls,follower,followed):
        cls.objects.create(follower=follower,followed=followed)
    @classmethod
    def unfollow_user(cls,follower,followed):
        cls.objects.filter(follower=follower,followed=followed).delete()
    @classmethod
    def is_follow_user(cls,follower,followed):
        return cls.objects.filter(follower=follower,followed=followed).exists()
    @classmethod
    def get_fol_count(cls,user):
        data={"followers":0,"followeds":0}
        followers=cls.objects.filter(followed=user).count()
        followeds=cls.objects.filter(follower=user).count()
        data.update({"followers":followers,"followeds":followeds})
        return data
    @classmethod
    def get_followers(cls,user):
        return cls.objects.filter(followed=user)
    @classmethod
    def get_followeds(cls,user):
        return cls.objects.filter(follower=user)
    @classmethod
    def get_followed_username(cls,user):
        followed=cls.get_followeds(user)
        return followed.values_list('followed__username',flat=True)
    class Meta:
        verbose_name_plural="Takipleşmeler"