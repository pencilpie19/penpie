#Coding by Muhammet Bulut - CEO of Pencil Pie
from django.contrib import admin
from django.urls import path
from . import views

app_name = "user"
urlpatterns = [
    path('members', views.reg, name="members"), #Kayıt ol / Giriş Yap sayfasına gider
    path('login', views.loginUser, name="login"), #Login işlemi aksiyonu
    path('logout', views.logoutUser, name="logout"), #Logout işlemi aksiyonu
    path('register', views.registerUser, name="register"), #Kayıt işlemi aksiyonu
    path('<str:username>', views.userProfile, name='profile'), #Profil sayfasına gider
    path('block/<str:username>', views.block_user, name='block'), #Engelleme aksiyonu 'ŞU AN KULLANILMIYOR'
    path('settings/', views.user_settings, name="settings"), #Ayarlar sayfasına gider
    path('yeter/<str:type>', views.yeter, name="yeter"), #Profil ve Kapak fotoğrafı değiştirme aksiyonu
    path('yeter2cover/', views.yeter2cover, name="yeter2cover"), #Kapak fotoğrafı aksiyonu 'ARTIK KULLANILMIYOR KAPAK VE PROFİL /yeter ADRESİNDEN GERÇEKLEŞİYOR"
    path('settings/passchange', views.user_password_change, name="passchange"), #Parola değiştirme aksiyonu
    path('followers/<str:username>',views.user_followers,name="followers"), #Takipçiler sayfasına gider
    path('followeds/<str:username>',views.user_followeds,name="followeds") #Takip edilenler sayfasına gider
]
