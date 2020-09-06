#Coding by Muhammet Bulut - CEO of Pencil Pie


from django.shortcuts import render
from django.http import HttpResponseBadRequest,JsonResponse
from django.shortcuts import get_object_or_404,Http404
from django.template.loader import render_to_string
from .models import Following
from django.contrib.auth.models import User

from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from user.models import Notifications,UserLog
# Create your views here.

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def follow_user(request):

    response=sub_follow_user(request)
    data=response.get("data")
    followed=response.get("followed")
    fol_count=Following.get_fol_count(followed)
    context={"user":followed,"follower_count":fol_count["followers"],"followed_count":fol_count["followeds"]}
    html=render_to_string("includes/following/folpart.html",context=context,request=request)
    data.update({"html":html})
    return JsonResponse(data=data)

def sub_follow_user(request):
    if not request.is_ajax():
        return HttpResponseBadRequest()
    data = {"follow_case":True,"html": "", 'is_valid': True, "msg": "Takipten Çık", "active": True}
    follower_username = request.GET.get("follower_username", None)
    followed_username = request.GET.get("followed_username", None)

    follower = get_object_or_404(User, username=follower_username)
    followed = get_object_or_404(User, username=followed_username)

    is_follow = Following.is_follow_user(follower=follower, followed=followed)

    if not is_follow:
        Following.follow_user(follower=follower, followed=followed)
        noti=Following.objects.filter(follower=follower,followed=followed)
        Notifications.add_notification(user=followed,obj=noti[0],request=request)
    else:
        noti=Following.objects.filter(follower=follower,followed=followed)
        Notifications.delete_notification(obj=noti[0],request=request)
        Following.unfollow_user(follower=follower, followed=followed)
        data.update({"msg": "Takip Eyle", "active": False,"follow_case":False})
    return {"data":data,"followed":followed}

def follow_modal_user(request):
    response=sub_follow_user(request)
    follow_type=request.GET.get("follow_type")
    owner=request.GET.get("owner")
    data=response.get("data")
    followed=response.get("followed")
    followers=Following.get_followeds(user=request.user)
    my_followed=Following.get_followed_username(user=request.user)
    fol_count = Following.get_fol_count(request.user)
    if owner==request.user.username:
        context = {"user": request.user, "follower_count": fol_count["followers"], "followed_count": fol_count["followeds"]}
        html_case = render_to_string("includes/following/folpart.html", context=context, request=request)
        html=render_to_string("includes/following/follist.html",context={
            "following":followers,"my_followed":my_followed,"follow_type":follow_type
        },request=request)
        data.update({"html":html,"html_case":html_case,"owner":True,"follow_type":follow_type})
    else:
        data.update({"owner":False})
    return JsonResponse(data=data)

def follower_or_followed_list(request,follow_type):
    data={"is_valid":True,"html":''}
    page=request.GET.get("page",1)
    follow_type=follow_type.strip()
    username=request.GET.get('username',None)
    if not username:

        raise Http404
    user=get_object_or_404(User,username=username)
    my_followed=Following.get_followed_username(user=request.user)
    if follow_type == 'followers':
        followers=Following.get_followers(user=user)
        followers=followers_and_followed_paginate(followers,page)
        html=render_to_string("includes/following/follist.html",context={
            "following":followers,"my_followed":my_followed,"follow_type":follow_type
        } , request=request)

        html_paginate=render_to_string("includes/following/button_includes/show_me_more.html",
                                       context={"username":user.username,"following":followers,"follow_type":follow_type})

    elif follow_type == 'followeds':
        followeds=Following.get_followeds(user=user)
        followeds=followers_and_followed_paginate(followeds,page)
        html=render_to_string("includes/following/follist.html",context={
            "following":followeds,"my_followed":my_followed,"follow_type":follow_type
        },request=request)
        html_paginate = render_to_string("includes/following/button_includes/show_me_more.html",
                                         context={"username":user.username,"following": followeds, "follow_type": follow_type})

    else:

        raise Http404
    data.update({"html":html,"html_paginate":html_paginate})
    return JsonResponse(data=data)

def followers_and_followed_paginate(queryset,page):
    paginator=Paginator(queryset,1)
    try:
        queryset=paginator.page(page)
    except PageNotAnInteger:
        queryset=paginator.page(1)
    except EmptyPage:
        queryset=paginator.page(paginator.num_pages)
    return queryset