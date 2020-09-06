#Coding by Muhammet Bulut - CEO of Pencil Pie

from django.contrib import admin
from django.urls import path
from . import views


app_name = "following"
urlpatterns = [
    path('low/', views.follow_user, name="follow"),
    path('lowmodal/', views.follow_modal_user, name="follow_modal"),
    path('low_list/<str:follow_type>', views.follower_or_followed_list, name="f_list"),
]