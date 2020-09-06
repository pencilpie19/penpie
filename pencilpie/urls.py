from django.contrib import admin
from django.urls import path,include
from mainpie import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ne-icindeyim-zamanin-ne-de-busbutun-disinda/', admin.site.urls),
    path('',views.index,name="index"),      #Genel manada index'in olduğun Mainpie app'inin içerisindeki view'dan çalışır
    path('user/', include("user.urls")),    #Kullanıcı işlemleri
    path('pie_thing/', include("pie_thing.urls")), #PieThing
    path('fol/', include("following.urls")),    #Takip etme işlemleri

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)