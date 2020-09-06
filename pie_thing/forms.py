#Coding by Muhammet Bulut - CEO of Pencil Pie

from django import forms
from .models import Comment,Thing,Report,Repost,SameThing,ThingReport,Help
from PIL import Image
from django import forms
from django.core.files import File


class ThingForm(forms.ModelForm):
    class Meta:
        model=Thing
        fields=["title","content","opt1","opt2"]

    def __init__(self,*args,**kwargs):
        super(ThingForm, self).__init__(*args, **kwargs)
        self.fields["title"].widget.attrs={"placeholder":"Tartışma Başlığı","max":30}
        self.fields["content"].widget.attrs={"placeholder":"Açıklama", "rows":"10"}
        self.fields["opt1"].widget.attrs={"placeholder":"Seçenek 1","max":12}
        self.fields["opt2"].widget.attrs={"placeholder":"Seçenek 2","max":12}
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}
class ContactForm(forms.ModelForm):
    class Meta:
        model=Help
        fields=["help_content"]
    def __init__(self,*args,**kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["help_content"].widget.attrs={"placeholder":"Mesajını buraya yaz.."}

class CommentForm(forms.ModelForm):

    class Meta:
        model=Comment
        fields=["content","photo","is_anon"]
    def __init__(self,*args,**kwargs):
        super(CommentForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields["is_anon"].widget.attrs={'style':'margin-left: 15px', 'type':'checkbox'}
            self.fields["photo"].widget.attrs={'class':'form-control'}
            self.fields["content"].widget.attrs={'class':'form-control',"cols":"50" ,"rows":"3"
                ,"placeholder":"Bu konu hakkındaki görüşleri ilet.."}

class ReportForm(forms.ModelForm):

    class Meta:
        model=Report
        fields=["report_content"]
    def __init__(self,*args,**kwargs):
        super(ReportForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}

class RepostForm(forms.ModelForm):

    class Meta:
        model=Repost
        fields=["repost_content"]
    def __init__(self,*args,**kwargs):
        super(RepostForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}

class SameForm(forms.ModelForm):

    class Meta:
        model=SameThing
        fields=["content"]
    def __init__(self,*args,**kwargs):
        super(SameForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}

class ThingRepForm(forms.ModelForm):
    class Meta:
        model=ThingReport
        fields=["content"]
    def __init__(self,*args,**kwargs):
        super(ThingRepForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs={'class':'form-control'}

class SearchForm(forms.Form):
    search=forms.CharField(max_length=500,required=False,widget=forms.TextInput(attrs={"placeholder":"PieThing'de Ara","class":"form-control"}))