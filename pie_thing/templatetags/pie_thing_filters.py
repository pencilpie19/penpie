from django import template
from datetime import date
from datetime import datetime

from django.utils.timesince import timesince

register = template.Library()

@register.filter(name='tarih_bukucu')
def tarih_bukucu(dt):
    year=dt.year
    day=dt.day
    month=dt.month

    return "{}/{}/{}".format(day,month,year)
@register.filter(name="short_date")
def short_date(dt):
    text=""
    ts=timesince(dt)
    liste=ts.split()
    if "yıl" in ts:
        text=liste[0]+"yıl"
    elif "ay" in ts:
        text=liste[0]+"ay"
    elif "hafta" in ts:
        text=liste[0]+"hafta"
    elif "gün" in ts:
        text=liste[0]+"g"
    elif "saat" in ts:
        text=liste[0]+"s"
    elif "dakika" in ts:
        if liste[0]=="0":
            text="Az önce"
        else:
            text=liste[0]+"d"
    return text

@register.filter(name="isim_bukucu")
def isim_bukucu(cls):#d
    return cls._meta.object_name