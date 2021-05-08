import datetime
import json
from datetime import timedelta
from random import randrange

from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotFound, HttpResponse

from .models import UserStat
from .forms import *


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)

            profile.user = user
            profile.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created')
            return redirect('login')
    else:
        form = UserRegisterForm()
        profile_form = ProfileForm()
    return render(request, 'users/register.html', {'form': form, 'profile_form': profile_form})


@csrf_exempt
def receive_data(request):
    if request.method == 'GET':
        return HttpResponseNotFound()
    #data = json.loads(request.data)
    data = json.loads(request.body.decode())
    date = timezone.now()
    stat = UserStat()
    stat.user = User.objects.get(pk=data['user_id'])
    stat.time_from = date
    stat.time_to = date
    stat.metrics = data
    stat.save()
    return HttpResponse(str(request.body))