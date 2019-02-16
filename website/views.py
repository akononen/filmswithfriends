from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from website.models import *
import json

def textinput(request):
    #saving input text to db
    if request.method == "POST":
        instance_text = Text()
        instance_text.input = request.POST['text']
        instance_text.save()

    #collecting all input texts
    text_list = Text.objects.all()

    #sending them as HttpResponse
    return render(request, "base.html", {'text_list': text_list})
