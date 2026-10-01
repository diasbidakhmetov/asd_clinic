from django.contrib import auth
from django.urls import reverse
from django.core.paginator import Paginator
from results.models import TestResults,TestTypes
from users.forms import UserLoginForm, UserRegisterForm
from django.shortcuts import render, HttpResponseRedirect
from results.models import Atec,Cars,EyeResults,MChat,SCQ,User,Casd
from scripts.get_iin import format_date,calculate_age
from users.forms import (
    UserLoginForm,
    UserRegisterForm,
    StaffUserRegisterForm,
)


def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            iin = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(request, iin=iin, password=password)

            if user:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('index'))
    else:
        form = UserLoginForm()

    context = {'form': form}
    return render(request, 'users/login.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UserRegisterForm()

    context = {'form': form}
    return render(request, 'users/register.html', context)


def staff_register(request):
    if request.method == 'POST':
        form = StaffUserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = StaffUserRegisterForm()

    context = {'form': form}
    return render(request, 'users/staff_register.html', context)


def profile(request,test_type_id=None,user_id=None):

    if user_id:
        form = User.objects.filter(iin = user_id).first()
        bday = format_date(str(form.b_day))
        age = calculate_age(str(form.b_day)) 
    else:
        form = request.user
        bday = format_date(str(form.b_day))
        age = calculate_age(str(form.b_day))
    
    context = {'title':'Жеке кабинет','form':form,'bday':bday,'age':age,
               'test_types':TestTypes.objects.all(),
               'test_type_id': test_type_id,
               'user_id': user_id,
               'form':form,
               }
    return render(request, 'users/profile.html',context)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))

def all_results(request,test_type_id=None,user_id=None,page=1):
    
    if user_id:
        form = User.objects.filter(iin = user_id).first()
    else:
        form = request.user


    if test_type_id:
        results = TestResults.objects.filter(test_type_id=test_type_id, iin = form.iin).order_by("-date_taken")
    else:
        results = TestResults.objects.filter(iin = form.iin).order_by("-date_taken")
    
    per_page = 10
    paginator = Paginator(results,per_page)
    results_paginator = paginator.page(page)
    
    context = {'title':'Нәтижелер',
               'results':results_paginator,
               'test_types':TestTypes.objects.all(),
               'test_type_id': test_type_id,
               'user_id': user_id,
               'form':form,
               }
    return render(request, 'users/all_results.html',context)


def test_card(request,user_id=None):
    
    if user_id:
        form = User.objects.filter(iin = user_id).first()
    else:
        form = request.user
    
    useriin = form.iin

    user = User.objects.get(iin=useriin)
    atec = Atec.objects.filter(result_id = TestResults.objects.filter(iin = user,test_type=TestTypes.objects.get(code_name='atec')).last()).last()
    cars = Cars.objects.filter(result_id = TestResults.objects.filter(iin = user,test_type=TestTypes.objects.get(code_name='cars')).last()).last()
    scq = SCQ.objects.filter(result_id = TestResults.objects.filter(iin = user,test_type=TestTypes.objects.get(code_name='scq')).last()).last()
    eye = EyeResults.objects.filter(result_id = TestResults.objects.filter(iin = user,test_type=TestTypes.objects.get(code_name='eye_tracking')).last()).last()
    m_chat = MChat.objects.filter(result_id = TestResults.objects.filter(iin = user,test_type=TestTypes.objects.get(code_name='m_chat')).last()).last()
    casd = Casd.objects.filter(result_id = TestResults.objects.filter(iin = user,test_type=TestTypes.objects.get(code_name='casd')).last()).last()
    tests = [atec,cars,scq,eye,m_chat,casd]
    

    context = {'title':'Нәтижелер',
               'tests':tests,
               'test_types':TestTypes.objects.all(),
               'user_id':user_id,
               'form':form,
               }
    return render(request, 'users/result_card.html',context)