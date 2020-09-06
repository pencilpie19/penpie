#Coding by Muhammet Bulut - CEO of Pencil Pie

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm
from .models import UserProfile
import re
from .models import Photo,CoverPhoto
from PIL import Image


class PhotoForm(forms.Form):
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(PhotoForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update(
            {'class': 'avatar-input', 'id': 'avatarInput', 'name': 'avatar_file'})
        self.fields['file'].label="Dosya"


class CoverPhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CoverPhotoForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields["file"].widget.attrs={"id":"cover_file","style":"display:none;"}
        self.fields["x"].widget.attrs={"id":"cid_x"}
        self.fields["y"].widget.attrs={"id":"cid_y"}
        self.fields["height"].widget.attrs={"id":"cid_height"}
        self.fields["width"].widget.attrs={"id":"cid_width"}

    class Meta:
        model = CoverPhoto
        fields = ('file', 'x', 'y', 'width', 'height', )
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'image/*'  # this is not an actual validation! don't rely on that!
            })
        }

#Giriş Formu
class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=50, label='Kullanıcı Adı/E-Posta',
                               widget=forms.TextInput(attrs={'class': 'form-control',"placeholder":"Kullanıcı Adı/E-Posta"}))
    password = forms.CharField(required=True, max_length=50, label='Parola',
                               widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Parola"}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Hatalı Kullanıcı Adı veya Şifre Girdiniz')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if re.match(r"[^@]+@[^@]+\.[^@]+", username):
            users = User.objects.filter(email__iexact=username)
            if len(users) > 0 and len(users) == 1:
                return users.first().username
        return username

nobody_can_get_these_usernames=["login","register","logout","members","block",
                                "settings","followers","followeds","bulut","muhammet"
                                ,"mbulut","canawear","muhammetbulut","ilker","kreytos","venom"]
class RegisterForm(forms.ModelForm):

    password = forms.CharField(min_length=5, required=True, label='Parola',
                               widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Parola"}))
    password_confirm = forms.CharField(min_length=5, label='Parolayı Doğrula',
                                       widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Parolayı Doğrula"}))
    gender=forms.ChoiceField(required=True,choices=UserProfile.GENDER,label="Cinsiyet")
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email','gender','password', 'password_confirm']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control input-group-lg'}
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['email'].widget.attrs={'style':"margin-right:20px;"}
        self.fields['gender'].widget.attrs={'style':"margin-left:20px;"}



    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password != password_confirm:
            self.add_error('password', 'Parolalar Eşleşmedi')
            self.add_error('password_confirm', 'Parolalar Eşleşmedi')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta sistemde kayıtlı')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu kullanıcı adı sistemde mevcut')
        if username in nobody_can_get_these_usernames:
            raise forms.ValidationError('Bu kullanıcı adını alamazsın')
        return username

class UserProfileUpdateForm(forms.ModelForm):
    gender=forms.ChoiceField(required=True,choices=UserProfile.GENDER,label="Cinsiyet")
    bio=forms.CharField(required=False,label="Hakkımda")
    birth_date=forms.DateField(input_formats=['%d/%m/%Y'],label="Doğum Tarihi (gg/aa/yyyy) şeklinde yazın.",widget=forms.DateInput(format='%d/%m/%Y'))
    email=forms.EmailField(required=True,label="E-Posta")
    class Meta:
        model=User
        fields=["first_name","last_name","username","email","gender","birth_date","bio"]

    def __init__(self, *args, **kwargs):
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower()

        if User.objects.filter(email=email).exclude(username=self.instance.username).exists():
            raise forms.ValidationError('Bu e-posta sistemde kayıtlı')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(username=self.instance.username).exists():
            raise forms.ValidationError('Bu kullanıcı adı sistemde mevcut')
        return username


class UserPasswordChangeForm(forms.Form):
    user=None
    old_password=forms.CharField(label="Mevcut Şifreniz",widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password=forms.CharField(label="Yeni Şifreniz",widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password_confirm=forms.CharField(label="Mevcut Şifreniz",widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def __init__(self,user,*args,**kwargs):
        self.user=user
        super(UserPasswordChangeForm, self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}
    def clean(self):
        newpassword=self.cleaned_data.get("new_password")
        newpasswordconfirm=self.cleaned_data.get("new_password_confirm")

        if newpassword!=newpasswordconfirm:
            self.add_error('new_password',"Şifreler eşleşmedi")
    def clean_old_password(self):
        old_password=self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Şifreniz hatalı")
        return old_password

class UserPasswordChangeForm2(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(UserPasswordChangeForm2, self).__init__(user, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class': 'form-control'}