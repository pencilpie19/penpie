#Coding by Muhammet Bulut - CEO of Pencil Pie
from django.shortcuts import render,redirect,reverse,get_object_or_404
from .forms import RegisterForm,LoginForm,UserProfile,UserPasswordChangeForm2,UserProfileUpdateForm,PhotoForm
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from following.models import Following
from django.contrib.auth.decorators import login_required
from .models import UserBlocking
# Create your views here.
from pie_thing.forms import RepostForm,ReportForm,ThingForm,SearchForm
from .models import Photo,CoverPhoto,UserLog
from .forms import PhotoForm,CoverPhotoForm
from .decorators import anonymous_required
import json
import os
from django.utils.six import BytesIO
from django.shortcuts import render
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse, HttpResponseRedirect
import sys

def compressImage(uploadedImage): #GELEN RESMİ SIKIŞTIRIR+BOYUTUNU KÜÇÜLTÜR
    imageTemproary = Image.open(uploadedImage)

    if imageTemproary.mode in ("RGBA", "P"):
        imageTemproary = imageTemproary.convert("RGB")
    outputIoStream = BytesIO()
    width, height = imageTemproary.size
    imageTemproaryResized = imageTemproary.resize((int(width / 1.2), int(height / 1.2)))  #BOYUT 1.2 ORANINDA KÜÇÜLTÜLÜR
    imageTemproaryResized.save(outputIoStream, format='JPEG', quality=50) #KALİTE 50% ORANINDA DÜŞER
    outputIoStream.seek(0)
    uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0],
                                         'image/jpeg', sys.getsizeof(outputIoStream), None)
    return uploadedImage

def yeter(request,type):
    form = PhotoForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        img_data = dict(request.POST.items())
        x = None # Coordinate x
        y = None # Coordinate y
        w = None # Width
        h = None # Height
        rotate = None # Rotate
        for key, value in img_data.items():
            if key == "avatar_data":
                str_value = json.loads(value)
                print(str_value)
                x = str_value.get('x')
                y = str_value.get('y')
                w = str_value.get('width')
                h = str_value.get('height')
                rotate = str_value.get('rotate')

        print('x: {}, y: {}, w: {}, h: {}, rotate: {}'.format(x, y, w, h, rotate))

        im = Image.open(request.FILES['file']).convert('RGBA')
        tempfile = im.rotate(-rotate, expand=True)
        tempfile = tempfile.crop((int(x), int(y), int(w+x), int(h+y)))
        tempfile_io = BytesIO()
        tempfile_io.seek(0, os.SEEK_END)
        tempfile.save(tempfile_io, format='PNG')
        image_file = InMemoryUploadedFile(tempfile_io, None, 'rotate.png', 'image/png', tempfile_io.tell(), None)
        image_file=compressImage(image_file)
        if type=="profile":
            Photo.objects.filter(user=request.user).delete()
            Photo.objects.create(user=request.user,file=image_file)
        elif type=="cover":
            CoverPhoto.objects.filter(user=request.user).delete()
            CoverPhoto.objects.create(user=request.user,file=image_file)

        data = {
            'result': True,
            'state': 200,
            'message': 'Yükleme Başarılı',
        }
        return JsonResponse({'data': data})
    else:
        print('Uncut image!')
        print(form.errors)

    return redirect('user:profile', request.user)

def yeter2cover(request):
    if request.method == 'POST':

        form = CoverPhotoForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            CoverPhoto.objects.filter(user=request.user).delete()
            photo=form.save(commit=False)
            photo.user=request.user
            photo.save()
            x = form.cleaned_data.get('x')
            y = form.cleaned_data.get('y')
            w = form.cleaned_data.get('width')
            h = form.cleaned_data.get('height')
            image = Image.open(photo.file)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((1030, 360), Image.ANTIALIAS)
            resized_image.save(photo.file.path)
            return redirect('user:profile', request.user)

@anonymous_required
def reg(request):
    loginForm=LoginForm(request.POST or None)   #Giriş Yap formu
    registerForm=RegisterForm(request.POST or None) #Kayıt Ol formu
    return render(request,"user/register.html",context={"log":loginForm,"reg":registerForm,"regActive":"active","logActive":""})
@anonymous_required
def loginUser(request):
    loginForm = LoginForm(request.POST or None)
    registerForm = RegisterForm(request.POST or None)
    if loginForm.is_valid():
        username = loginForm.cleaned_data.get('username')
        password = loginForm.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, "Başarıyla Giriş yaptunuz.")
                return redirect('pie_thing:index')
    return render(request, "user/register.html", context={"log": loginForm, "reg": registerForm,"regActive":"","logActive":"active"})


@anonymous_required
def registerUser(request):
    loginForm = LoginForm(request.POST or None)
    registerForm = RegisterForm(request.POST or None)
    if registerForm.is_valid():
        user=registerForm.save(commit=False)
        password=registerForm.cleaned_data.get('password')
        username=registerForm.cleaned_data.get('username')

        gender=registerForm.cleaned_data.get('gender')
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user,gender=gender,bio="Merhaba ben {}".format(username))
        user.save()
        user=authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                messages.success(request,"Tebrikler başarıyla kaydınız gerçekleşti")
                return redirect('user:settings')



    return render(request,"user/register.html",context={"log": loginForm, "reg": registerForm,"regActive":"active","logActive":""})

def logoutUser(request): #Çıkış işlemi
    logout(request)
    return redirect("user:members")

@login_required(login_url="user:login")
def userProfile(request,username):
    response = HttpResponseRedirect('/')
    response.delete_cookie('_gat', domain='pencilpie.com')
    response.delete_cookie('_ga', domain='pencilpie.com')
    response.delete_cookie('_gid', domain='pencilpie.com')
    is_follow = False
    search_form = SearchForm(data=request.GET or None)
    usero=get_object_or_404(User,username=username)
    activities=UserLog.objects.filter(is_active=True,user=usero).order_by("-activity_date")[:5]
    ppform=PhotoForm()
    cpform=CoverPhotoForm()
    repost_form = RepostForm()
    report_form = ReportForm()
    thing_form = ThingForm()
    user = get_object_or_404(User, username=username)
    follower=Following.is_follow_user(request.user,user)
    is_follow_me = Following.is_follow_user(user, request.user)
    foll_count = Following.get_fol_count(user)
    follower_count = foll_count["followers"]
    followed_count = foll_count["followeds"]
    if user != request.user:
        is_follow = Following.is_follow_user(follower=request.user, followed=user)

    if search_form.is_valid():
        arama=search_form.cleaned_data.get("search",None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))

    return render(request,"user/profile.html",context={"activities":activities,"search_form":search_form,"is_follow_me":is_follow_me,"isfollow":follower,"thing_form":thing_form,"repost_form":repost_form,"report_form":report_form,"cpform":cpform,"ppform":ppform,"follower_count":follower_count,"followed_count":followed_count,"is_follow":is_follow,"user":user})

@login_required(login_url="user:login")
def user_followers(request,username):
    user=get_object_or_404(User,username=username)
    followers=Following.get_followers(user)
    ppform = PhotoForm()
    cpform = CoverPhotoForm()
    search_form = SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    usero = get_object_or_404(User, username=username)
    activities = UserLog.objects.filter(is_active=True, user=usero).order_by("-activity_date")[:5]
    return render(request,"user/followers.html",context={"activities":activities,"cpform":cpform,"ppform":ppform,"search_form":search_form,"user":user,"followers":followers})

@login_required(login_url="user:login")
def user_followeds(request,username):
    user = get_object_or_404(User, username=username)
    followers = Following.get_followeds(user)
    ppform = PhotoForm()
    cpform = CoverPhotoForm()
    search_form = SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    usero = get_object_or_404(User, username=username)
    activities = UserLog.objects.filter(is_active=True, user=usero).order_by("-activity_date")[:5]
    return render(request, "user/followeds.html", context={"activities":activities,"cpform":cpform,"ppform":ppform,"search_form":search_form,"user": user, "followers": followers})

@login_required(login_url="user:login")
def user_password_change(request):
    is_follow=False
    form=UserPasswordChangeForm2(request.user,request.POST or None)
    user = get_object_or_404(User, username=request.user.username)
    foll_count = Following.get_fol_count(user)
    follower_count = foll_count["followers"]
    followed_count = foll_count["followeds"]
    ppform = PhotoForm()
    cpform = CoverPhotoForm()
    activities = UserLog.objects.filter(is_active=True, user=request.user).order_by("-activity_date")[:5]
    if user != request.user:
        is_follow = Following.is_follow_user(follower=request.user, followed=user)
    if request.method=="POST":
        if form.is_valid():
            user = form.save(commit=True)
            update_session_auth_hash(request, user)
            messages.success(request, 'Tebrikler Şifreniz Başarıyla Güncellendi')
            return redirect(request.user.userprofile.get_user_url())
        else:
            messages.warning(request,"Lütfen aşağıdaki uyarılara dikkat edin.")
            return render(request, "user/passchange.html", context={"activities":activities,"cpform":cpform,"ppform":ppform,"follower_count":follower_count,"followed_count":followed_count,"is_follow":is_follow,"form": form})

    search_form = SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))
    return render(request,"user/passchange.html",context={"activities":activities,"search_form":search_form,"cpform":cpform,"ppform":ppform,"follower_count":follower_count,"followed_count":followed_count,"is_follow":is_follow,"form":form})

@login_required(login_url="user:login")
def user_settings(request):
    is_follow=False
    gender=request.user.userprofile.gender
    bio=request.user.userprofile.bio
    birth_date=request.user.userprofile.birth_date
    initial={"gender":gender,"bio":bio,"birth_date":birth_date}
    form=UserProfileUpdateForm(request.POST or None, request.FILES or None,instance=request.user,initial=initial)
    ppform = PhotoForm()
    cpform = CoverPhotoForm()
    activities = UserLog.objects.filter(is_active=True, user=request.user).order_by("-activity_date")[:5]
    if form.is_valid():
        user=form.save(commit=True)
        gender=form.cleaned_data.get("gender",None)
        bio=form.cleaned_data.get("bio",None)
        birth_date=form.cleaned_data.get("birth_date",None)

        user.userprofile.gender=gender
        user.userprofile.bio=bio
        user.userprofile.birth_date=birth_date
        user.userprofile.save()
        messages.success(request,"Tebrikler profiliniz başarıyla güncellendi")
        return redirect(user.userprofile.get_user_url())
    user = get_object_or_404(User, username=request.user.username)
    foll_count = Following.get_fol_count(user)
    follower_count = foll_count["followers"]
    followed_count = foll_count["followeds"]
    if user != request.user:
        is_follow = Following.is_follow_user(follower=request.user, followed=user)
    search_form = SearchForm(data=request.GET or None)
    if search_form.is_valid():
        arama = search_form.cleaned_data.get("search", None)
        if arama:
            return redirect(reverse('pie_thing:index') + '?search={}'.format(arama))

    return render(request,"user/settings.html",context={"activities":activities,"cpform":cpform,"ppform":ppform,"search_form":search_form,"follower_count":follower_count,"followed_count":followed_count,"is_follow":is_follow,"form":form})

@login_required(login_url="user:login")
def user_about(request,username):
    is_follow=False
    user=get_object_or_404(User,username=username)
    foll_count = Following.get_fol_count(user)
    follower_count = foll_count["followers"]
    followed_count = foll_count["followeds"]
    if user != request.user:
        is_follow = Following.is_follow_user(follower=request.user, followed=user)
    return render(request,"user/about.html",context={"follower_count":follower_count,"followed_count":followed_count,"is_follow":is_follow,"user":user})

@login_required(login_url="user:login")
def user_river(request,username):
    is_follow = False
    user = get_object_or_404(User, username=username)
    foll_count = Following.get_fol_count(user)
    follower_count = foll_count["followers"]
    followed_count = foll_count["followeds"]
    if user != request.user:
        is_follow = Following.is_follow_user(follower=request.user, followed=user)
    return render(request,"user/river.html",context={"follower_count":follower_count,"followed_count":followed_count,"is_follow":is_follow,"user":user})

@login_required(login_url="user:login")
def block_user(request,username):
    user=get_object_or_404(User,username=username)
    UserBlocking.objects.create(blocker=request.user,blocked=user)
    return redirect("pie_thing:index")