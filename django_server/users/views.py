import json

import dateutil.parser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *
from .config import *


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        # profile_form = ProfileForm(request.POST)

        if form.is_valid():  # and profile_form.is_valid():
            user = form.save()
            # profile = profile_form.save(commit=False)

            # user.profile.employer_key = profile.employer_key
            user.profile.save()
            # profile.user = user
            # profile.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created')
            return redirect('login')
    else:
        form = UserRegisterForm()
        # profile_form = ProfileForm()
    return render(request, 'users/register.html', {'form': form,
                                                   # 'profile_form': profile_form
                                                   })


@csrf_exempt
def receive_data(request):
    if request.method == 'GET':
        return HttpResponseNotFound()

    data = json.loads(request.body.decode())
    if 'token' not in data or 'time_from' not in data or 'time_to' not in data:
        return HttpResponseNotFound("'token', 'time_from' or 'time_to' are not in received data")

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
    if 'username' not in data or 'password' not in data:
        return HttpResponseNotFound("'username' or 'password' are not in received data")
    user = get_object_or_404(User, username=data['username'])
    if not user.check_password(data['password']):
        return HttpResponse('Invalid password', status=401)

    return JsonResponse({"token": user.useruniquetoken.token})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid():  # and p_form.is_valid():
            u_form.save()
            # p_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        # p_form = ProfileForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        # 'p_form': p_form
    }

    return render(request, 'users/profile.html', context)


@csrf_exempt
def all_metrics(request):
    return JsonResponse({
        CHAR_COUNTER: [m.char for m in CharCountingMetric.objects.all()],
        WORD_COUNTER: [m.substring for m in SubstringCountingMetric.objects.all()]
    })


@csrf_exempt
def user_metrics(request):
    if request.method == 'GET':
        return HttpResponseNotFound()

    data = json.loads(request.body.decode())
    if 'token' not in data:
        return HttpResponseNotFound("'token' is absent in received data")

    user = get_object_or_404(UserUniqueToken, token=data['token']).user
    metrics = list(user.profile.get_metrics().keys())
    param_metric = [
        m.name for m in
        CharCountingMetric.objects.filter(name__in=metrics)
    ] + [
        m.name for m in
        SubstringCountingMetric.objects.filter(name__in=metrics)
    ] + [
        m.name for m in
        SpecificBranchCommitCounterMetric.objects.filter(name__in=metrics)
    ] + [
        m.name for m in
        SpecificLengthPasteCounterMetric.objects.filter(name__in=metrics)
    ] + [
        m.name for m in
        SpecificLengthCopyCounterMetric.objects.filter(name__in=metrics)
    ]

    non_param_metric = [
        m.string_representation for m in
        Metric.objects.exclude(name__in=param_metric).filter(name__in=metrics)
    ]
    return_dict = {}
    for string_representation in non_param_metric:
        return_dict[string_representation] = string_representation
    return_dict[SPECIFIC_LENGTH_COPY_COUNTER] = [
        m.substring_length for m in
        SpecificLengthCopyCounterMetric.objects.filter(name__in=metrics)
    ]
    return_dict[SPECIFIC_LENGTH_PASTE_COUNTER] = [
        m.substring_length for m in
        SpecificLengthPasteCounterMetric.objects.filter(name__in=metrics)
    ]
    return_dict[CHAR_COUNTER] = [
        m.char for m in
        CharCountingMetric.objects.filter(name__in=metrics)
    ]
    return_dict[WORD_COUNTER] = [
        m.substring for m in
        SubstringCountingMetric.objects.filter(name__in=metrics)
    ]
    return_dict[SPECIFIC_BRANCH_COMMIT_COUNTER] = [
        m.branch_name for m in
        SpecificBranchCommitCounterMetric.objects.filter(name__in=metrics)
    ]
    return JsonResponse(return_dict)
