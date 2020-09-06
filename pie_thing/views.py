#Coding by Muhammet Bulut - CEO of Pencil Pie
from itertools import chain
from random import uniform, random, choice, sample

from django.db.models import Value as V
import datetime
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Concat
from django.shortcuts import render,HttpResponse,redirect,get_object_or_404,reverse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.decorators.csrf import csrf_protect
from docutils.nodes import comment
from operator import attrgetter

from jsonfield import json

from .forms import CommentForm,ThingForm,ReportForm,RepostForm,SameForm,SearchForm,ThingRepForm,ContactForm
from .models import Comment,Thing,SupportComment,Report,Repost,SameThing,ThingReport,Help
from following.models import Following
from user.models import User,ProfileRiver,Notifications,UserLog
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse, Http404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def paginateComment(request,list):
    #numbers_list = range(1, 100)
    page = request.GET.get('page', 1)

    paginator = Paginator(list, 10)
    try:
        numbers = paginator.page(page)
    except PageNotAnInteger:
        numbers = paginator.page(1)
    except EmptyPage:
        numbers = paginator.page(paginator.num_pages)

    return numbers

def get_comments_on_anywhere(user):

    content_type = ContentType.objects.get_for_model(Thing)
    user = User.objects.get(username=user.username)
    listemiz = list(Following.get_followed_username(user))
    listemiz.append(user)
    comments = Comment.objects.filter(user__username__in=listemiz,content_type=content_type).order_by("-created_date")
    things=Thing.objects.filter(author__username__in=listemiz).order_by("-created_date")
    if comments and things:
        result_list = sorted(
            chain(things, comments),
            key=lambda instance: instance.created_date)[::-1]
        print(result_list[0]._meta.object_name)
        return result_list
    else:
        return False

def get_post_on_anywhere(user):
    user = User.objects.get(username=user.username)
    listemiz = list(Following.get_followed_username(user))

    posts = Comment.objects.filter(user__username__in=listemiz)
    return posts


def get_thing_on_anywhere():
    thing_3 = Thing.objects.all().order_by("-created_date")
    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

    thing_3=Thing.objects.filter(created_date__range=(today_min, today_max))

    thing_3_s = sorted(thing_3, key=lambda t: t.get_comment_count())[::-1]
    thing_3_s=thing_3_s[:3]


    randomly = Thing.objects.all()
    liste=set([i for i in thing_3_s])
    thing_3_n = Thing.objects.all().order_by("-created_date")[:3]
    for i in thing_3_n:
        liste.add(i)
    while True:
        liste.add(choice(randomly))
        if len(liste)==8:
            break

    return list(liste)[::-1]
    # change 3 to how many random items you want
@login_required(login_url="user:login")
def index(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('_gat', domain='pencilpie.com')
    response.delete_cookie('_ga', domain='pencilpie.com')
    response.delete_cookie('_gid', domain='pencilpie.com')
    get_thing_on_anywhere()
    thing_title=get_thing_on_anywhere()
    thing_form=ThingForm()
    search_form=SearchForm(data=request.GET or None)
    report_form = ReportForm()
    repost_form = RepostForm()


    if not get_comments_on_anywhere(request.user):
        posts="YOK"
    else:
        posts=paginateComment(request,list(get_comments_on_anywhere(request.user)))

    if search_form.is_valid():
        print("ilk aşama")
        arama=search_form.cleaned_data.get("search",None)
        if arama:
            print("ikinci aşama")

            comments=Comment.objects.filter(Q(content__icontains=arama))
            things=Thing.objects.filter(Q(title__icontains=arama) | Q(content__icontains=arama))
            users = User.objects.annotate(
                full_name=Concat('first_name', V(' '), 'last_name')
            ).filter(
                Q(full_name__icontains=arama) |
                Q(first_name__icontains=arama) |
                Q(last_name__icontains=arama) |
                Q(username__icontains=arama)
            )
            #users=User.objects.filter(Q(username__icontains=arama) | Q(first_name__icontains=arama) | Q(last_name__icontains=arama))

            return render(request, "pie_thing/index.html",
                          {"is_search":True,"tt": thing_title, "search_form": search_form, "thing_form": thing_form, "comments": comments, "things":things,"users":users,
                           "report_form": report_form, "repost_form": repost_form})

    return render(request,"pie_thing/index.html",{"is_search":False,"tt":thing_title,"search_form":search_form,"thing_form":thing_form,"posts":posts,"report_form":report_form,"repost_form":repost_form})

#@login_required(login_url="user:login")
def comment(request,id):
    comment=get_object_or_404(Comment,id=id)
    report_form = ReportForm()
    repost_form = RepostForm()
    thing_title = get_thing_on_anywhere()
    search_form = SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    return render(request,"pie_thing/comment.html",{"search_form":search_form,"tt":thing_title,"comment":comment,"report_form":report_form,"repost_form":repost_form})

@login_required(login_url="user:login")
def contact(request):
    form=ContactForm(request.POST or None)
    thing_title = get_thing_on_anywhere()
    search_form = SearchForm(data=request.GET or None)

    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    if form.is_valid():
        mes=form.save(commit=False)
        mes.user=request.user
        mes.save()
        return redirect("pie_thing:index")
    return render(request,"pie_thing/contact.html",{"form":form,"tt":thing_title,"search_form":search_form})

@login_required(login_url="user:login")
def addThing(request):
    form = ThingForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        thing = form.save(commit=False)
        thing.author = request.user
        thing.save()
        UserLog.add_log(obj=thing,user=request.user,ip_adress=str(get_client_ip(request)))
        return redirect("pie_thing:thing",id=thing.id)

def list_t(request):
    things = Thing.objects.all().order_by("-created_date")
    thing_title = get_thing_on_anywhere()
    search_form=SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    return render(request,"pie_thing/thing_list.html", {"things":things,"search_form":search_form,"tt":thing_title})

def thing(request,id):
    thing = get_object_or_404(Thing, id=id)
    form=CommentForm()
    report_form=ReportForm()
    repost_form=RepostForm()
    same_form=SameForm()
    thing_title = get_thing_on_anywhere()
    rt_form=ThingRepForm()

    search_form = SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    return render(request, "pie_thing/thing.html", {"search_form":search_form,"rt_form":rt_form,"tt":thing_title,"thing": thing,"form":form,"report_form":report_form,"repost_form":repost_form,"same_form":same_form})

@login_required(login_url="user:login")
def explore(request):
    user = User.objects.get(username=request.user.username)
    listemiz = list(Following.get_followed_username(user))
    print(type(listemiz))
    comments = Comment.objects.filter(user__username__in=listemiz)
    pass

@login_required(login_url="user:login")
def notifications(request):
    thing_title = get_thing_on_anywhere()
    noti=Notifications.objects.filter(user=request.user).order_by("-notification_date")
    search_form = SearchForm(data=request.GET or None)
    context={"tt":thing_title,"noti":noti,"search_form":search_form}
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    return render(request,"pie_thing/notifications.html",context)

@login_required(login_url="user:login")
def read_noti(request):
    noti=Notifications.objects.filter(user=request.user)
    for i in noti:
        i.is_unread=False
        i.save()
    return JsonResponse({})

@login_required(login_url="user:login")
def add_comment(request,id,model_type,options,type):
    data={"is_valid":True,"thing_comment_html":"","model_type":model_type}
    obj=None
    progress_bar=None

    form=CommentForm(data=request.POST,files=request.FILES)
    if model_type=="thing":
        obj=get_object_or_404(Thing,id=id)
    elif model_type=="comment":
        obj=get_object_or_404(Comment,id=id)
    else:
        Http404
    if form.is_valid():
        photo=form.cleaned_data.get("photo")

        content=form.cleaned_data.get("content")
        is_anon=form.cleaned_data.get("is_anon")
        Comment.add_comment(obj,model_type,request.user,content,options,photo,str(get_client_ip(request)),request,is_anon)


    if type=="thing":
        comment_html=render_to_string("includes/comment/comment-list-partial.html",context={
            "thing":obj,
            "request":request
        })
        progress_bar=render_to_string("includes/progress/progress.html",context={
            "thing":obj,
            "request":request
        })
    elif type=="news":
        comment_html=render_to_string("includes/news_river/news_river.html",context={
            "request":request,
            "comments":get_comments_on_anywhere(request.user)
        })
        return redirect("pie_thing:comment",id=obj.id)
    elif type=="child":
        """comment_html = render_to_string("includes/comment/comment-list-partial.html", context={
            "thing": obj,
            "request": request
        })"""

        comment_html=render_to_string("includes/comment/single-comment.html",context={
            "comment":obj,
            "thing":obj.content_object
        })
    elif type=="single":
        comment_html=render_to_string("includes/comment/child-review.html",context={
            "comment":obj,
        })
    else:
        user=get_object_or_404(User,username=type)
        comment_html = render_to_string("includes/profile_river/river_list.html", context={
            "thing": obj,
            "request": request,
            "user":user,
        })
    data.update({
        "thing_comment_html":comment_html,
        "progress":progress_bar,
    })

    return JsonResponse(data=data)

@login_required(login_url="user:login")
def report_comment(request,id):
    report = ReportForm(request.POST or None)
    comment=get_object_or_404(Comment,id=id)
    if report.is_valid():
        content=report.cleaned_data.get("report_content")
        Report.objects.create(comment=comment, user=request.user, report_content=content)
    else:
        print("hayat bi else")
    return redirect("pie_thing:index")

@login_required(login_url="user:login")
def same_thing(request,id):
    same = SameForm(request.POST or None)
    thing=get_object_or_404(Thing,id=id)
    if same.is_valid():
        content=same.cleaned_data.get("content")
        SameThing.objects.create(thing=thing, user=request.user, content=content)
    else:
        print("hayat bi else")
    return redirect("pie_thing:index")

@login_required(login_url="user:login")
def report_thing(request,id):
    same = ThingRepForm(request.POST or None)
    thing=get_object_or_404(Thing,id=id)
    if same.is_valid():
        content=same.cleaned_data.get("content")
        ThingReport.objects.create(thing=thing, user=request.user, content=content)
    else:
        print("hayat bi else")
    return redirect("pie_thing:index")

@login_required(login_url="user:login")
def get_child_comment_form(request,type):
    data={"form-html":""}
    comment_id=request.GET.get("comment_id")
    typo=request.GET.get("typo",1)

    comment=get_object_or_404(Comment,id=comment_id)
    form=CommentForm()
    if typo=="typo":
        print("type zero")
        form_html = render_to_string("includes/comment/child-comment-for-single.html", context={
            "form": form,
            "comment": comment,
            "type": type

        }, request=request)
        data.update({
            "form_html": form_html
        })
    else:
        print("type hermano :)")
        form_html = render_to_string("includes/comment/child-comment-form.html", context={
            "form": form,
            "comment": comment,
            "type": type

        }, request=request)
        data.update({
            "form_html": form_html
        })

    return JsonResponse(data=data)

@login_required(login_url="user:login")
def get_comment_form(request):
    data={"form-html":""}
    opt_type=request.GET.get("opt")
    id=request.GET.get("id")
    thing=get_object_or_404(Thing,id=id)
    form=CommentForm()
    if opt_type=="opt1":
        op=1
        opt_type=thing.opt1
    elif opt_type=="opt2":
        op=2
        opt_type=thing.opt2
    elif opt_type=="opt3":
        op=3
        opt_type=thing.opt3
    form_html=render_to_string("includes/comment/comment-form.html",context={
        "form":form,
        "thing":thing,
        "opt":opt_type,
        "options":op,
    },request=request)

    data.update({
        "form_html":form_html
    })
    return JsonResponse(data=data)

@login_required(login_url="user:login")
def get_repost(request,id):
    data={"form-html":""}
    form=RepostForm()
    comment=get_object_or_404(Comment,id=id)
    form_html = render_to_string("includes/posting/reposting_comment.html", context={
        "form": form,
        "comment": comment,
    }, request=request)
    data.update({
        "form_html": form_html
    })
    return JsonResponse(data=data)

@login_required(login_url="user:login")
def repost(request,id):
    repost = RepostForm(request.POST or None)
    comment = get_object_or_404(Comment, id=id)
    if repost.is_valid():
        content = repost.cleaned_data.get("repost_content")
        pfrep=Repost.objects.create(reposting_comment=comment, user=request.user, repost_content=content)
        Notifications.add_notification(user=comment.user,obj=pfrep,request=request)
        ProfileRiver.add_river(pfrep,user=request.user)
    else:
        print("hayat bi else")
    return redirect("pie_thing:index")

def delete_repost(request,id):
    repost=get_object_or_404(Repost,id=id)
    ProfileRiver.delete_river(obj=repost,user=request.user)
    Notifications.delete_notification(obj=repost,request=request)
    repost.delete()
    return JsonResponse({})


@login_required(login_url="user:login")
def delete_comment(request,id,obj):
    comment = get_object_or_404(Comment, id=id)
    cc=Comment.objects.filter(id=id)

    ProfileRiver.delete_river(obj=cc[0],user=request.user)
    UserLog.delete_log(obj=cc[0],user=request.user)
    if comment.get_child_comment_count() !=0:
        for i in comment.get_child_comment():
            Notifications.delete_notification(obj=i,request=request)
            i.delete()
    if comment.get_un_sup_count() != 0 or comment.get_sup_count() !=0:
        for i in comment.sups.all():
            Notifications.delete_notification(obj=i,request=request)
    if comment.reposts.count()!=0:
        for i in comment.reposts.all():
            ProfileRiver.delete_river(obj=i,user=i.user)
    Notifications.delete_notification(obj=comment,request=request)
    comment.delete()
    if obj==0:
        return redirect("user:profile",request.user.username)
    elif obj==2:
        child_html = render_to_string("includes/comment/child-review.html", context={"comment": comment.content_object},
                                request=request)
        return JsonResponse({"child_html":child_html})
    else:
        return redirect("pie_thing:thing",id=obj)

from functools import wraps
from django.core.exceptions import PermissionDenied

@login_required(login_url="user:login")
def add_or_remove_sup(request,id,sup_type):
    data={"status":"deleted"}
    comment=get_object_or_404(Comment,id=id)
    sup_comment=SupportComment.objects.filter(comment=comment,user=request.user,sup_type=sup_type)
    anti_comment=SupportComment.objects.filter(comment=comment,user=request.user,sup_type= not sup_type)
    if sup_comment.exists(): #VAR OLAN OY GERİ ÇEKİLİR
        Notifications.delete_notification(obj=sup_comment[0],request=request)
        UserLog.delete_log(obj=sup_comment[0],user=request.user)
        sup_comment.delete()
        if sup_type == 1:
            comment.point = comment.point - 1
            comment.save()
        else:
            comment.point = comment.point + 1
            comment.save()

    else:
        if anti_comment.exists():
            Notifications.delete_notification(obj=anti_comment[0],request=request)
            UserLog.delete_log(obj=anti_comment[0],user=request.user)
            anti_comment.delete()
            noti=SupportComment.objects.create(comment=comment, user=request.user, sup_type=sup_type)
            if comment.user != request.user:
                Notifications.add_notification(user=comment.user, obj=noti,request=request)
            UserLog.add_log(obj=noti,user=request.user,ip_adress=str(get_client_ip(request)))
            data.update({"status": "added"})

            if sup_type==1:
                comment.point = comment.point + 2
                comment.save()
            else:
                comment.point = comment.point - 2
                comment.save()
        else:
            noti=SupportComment.objects.create(comment=comment,user=request.user,sup_type=sup_type)
            Notifications.add_notification(user=comment.user, obj=noti,request=request)
            UserLog.add_log(obj=noti,user=request.user,ip_adress=str(get_client_ip(request)))

            if sup_type==1:
                comment.point = comment.point + 1
                comment.save()
            else:

                comment.point = comment.point - 1
                comment.save()
            data.update({"status":"added"})


    html = render_to_string("includes/supporting/comment_reaction.html", context={"comment":comment}, request=request)
    count=comment.get_sup_count()
    data.update({"count":count})
    return JsonResponse({"reaction_html":html})

@login_required(login_url="user:login")
def comment_sup_list_user(request,id):

    comment=get_object_or_404(Comment,id=id)
    user_list=comment.get_sup_user_as_object()
    html=render_to_string("includes/supporting/comment_sup_list.html",context={
        "user_list":user_list},request=request
    )
    return JsonResponse(data={"html":html})