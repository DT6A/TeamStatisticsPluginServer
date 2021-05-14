import json

import dateutil.parser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)

            user.profile.employer_key = profile.employer_key
            user.profile.save()
            #profile.user = user
            #profile.save()

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

    data = json.loads(request.body.decode())
    #date = timezone.now()
    stat = UserStat()
    user = get_object_or_404(UserUniqueToken, token=data['token']).user
    stat.user = user
    stat.time_from = dateutil.parser.parse(data['time_from'])
    stat.time_to = dateutil.parser.parse(data['time_to'])

    del data['time_to']
    del data['time_from']
    del data['token']

    stat.metrics = data
    stat.save()
    return HttpResponse("Ok")


@csrf_exempt
def plugin_login(request):
    if request.method == 'GET':
        return HttpResponseNotFound()

    data = json.loads(request.body.decode())
    user = get_object_or_404(User, username=data['username'])
    if not user.check_password(data['password']):
        return HttpResponse('Invalid password', status=401)

    return JsonResponse({"token": user.useruniquetoken.token})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)
