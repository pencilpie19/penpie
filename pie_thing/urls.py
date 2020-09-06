#Coding by Muhammet Bulut - CEO of Pencil Pie
from django.contrib import admin
from django.urls import path
from . import views

app_name = "pie_thing"
urlpatterns = [
    path('', views.index, name="index"),
    path('thing/<int:id>', views.thing, name="thing"),              #Tartışma sayfasına gider
    path('addThing', views.addThing, name="addThing"),              #Tartışma ekleme aksiyonu
    path('deleteComment/<int:id>/<int:obj>',views.delete_comment,name="delete_comment"), #Yorum silme aksiyonu (ajax)
    path('report_comment/<int:id>',views.report_comment,name="report_comment"),          #Yorum raporlama aksiyonu (ajax)
    path('add_comment/<int:id>/<str:model_type>/<str:options>/<str:type>',views.add_comment,name="add_comment"), #Yorum ekleme aksiyonu (ajax)
    path('get-child-comment-form/<str:type>',views.get_child_comment_form,name="get-child-comment-form"), #Yavru yorum formu getirir (ajax)
    path('get-comment-form',views.get_comment_form,name="get-comment-from"), #Tartışma sayfasındaki ana yorum formunu getirir(ajax)
    path('supstaff/<int:id>/<int:sup_type>', views.add_or_remove_sup, name="supstaff"), #Oylama işlemleri gerçekleşir (ajax)
    path('supstaff/list/<int:id>', views.comment_sup_list_user, name="sup_list"), #Oy verenlerin listesini getirir 'ŞU AN KULLANILMIYOR'
    path('anchor/<int:id>', views.get_repost,name="anchor"), #Alıntılama işlemi için alıntılacak yorumu ve alıntı formunu getirir (ajax)
    path('repost/<int:id>', views.repost,name="repost"), #Alıntılama işlemini gerçekleştirir (ajax)
    path('delete_repost/<int:id>', views.delete_repost,name="delete_repost"), #Yorum silme aksiyonu (ajax)
    path('same/<int:id>', views.same_thing,name="same_thing"), #Aynı tartışma şikayeti oluşturma aksiyonu (ajax)
    path('repthing/<int:id>', views.report_thing,name="repthing"), #Tartışma raporlama aksiyonu (ajax)
    path('explore',views.explore,name="explore"), #Keşfet kısmını getirir 'ŞU AN KULLANILMIYOR'
    path('comment/<int:id>',views.comment,name="comment"), #Tek yorum sayfasına gider
    path('notifications',views.notifications,name="notifications"), #Bildirimler sayfasına gider
    path('read_noti',views.read_noti,name="read_noti"), #Bildirimler sayfasına gidildiğinde bildirimler okunmuş olur (ajax)
    path('list_t',views.list_t,name="list_t"), #Tartışmalar listesi sayfasına gider
    path('contact',views.contact,name="contact") #Bize Ulaş sayfasına gider.


]
