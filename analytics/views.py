from django.shortcuts import render
from users.models import User
from scripts.get_iin import calculate_average_age_from_db
from django.db.models import Avg
from django.db.models import Count
from results.models import Atec,MChat,SCQ,Cars,TestResults,EyeResults,MChatRiskLevel
from results.models import MChatRiskLevel, AtecDescriptions,CarsDescriptions,EyeDescription,SCQDescriptions
from results.models import CarsAnswers, AtecAnswers
from analytics.stat import get_desc_statistics
from django.db.models import Q
from results.models import TestTypes
from analytics.scripts import get_test_description,get_test_stats,get_total_anwsers,get_total_anwer_per_question,get_eyecount_stats,get_eye_zone_sums_by_image
from django.http import JsonResponse
from users.models import User
from django.core.paginator import Paginator
from results.models import Casd,CasdAnswers,CasdDescriptions,CasdQuestions


def patients(request,page=1):
    test_types = TestTypes.objects.all()
    patient_iin = request.GET.get("iin")

    all_users = User.objects.filter(role=1)
    
    if patient_iin:
        all_users = User.objects.filter(iin = patient_iin,role=1)
    
    per_page = 15
    paginator = Paginator(all_users,per_page)
    results_paginator = paginator.page(page)

    context = {
        'code': 'patients',
        'title': 'Пациенттер',
        'patients':results_paginator,
        'test_types': test_types,
    }
    return render(request, 'analytics/base_analysis.html', context)



def search_users(request):
    query = request.GET.get('q', '')
    role_id = request.GET.get('role_id')

    filters = Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(father_name__icontains=query)
    users = User.objects.filter(filters)

    if role_id:
        users = users.filter(role_id=1)

    users = users[:10]

    data = [
        {'iin': user.iin, 'full_name': str(user)} 
        for user in users 
        if str(user) is not None
    ]

    return JsonResponse(data, safe=False)


def standard_tests_analysis(request, test_type_id=None):
    test_types = TestTypes.objects.all()

    test_description = None
    filter_type = request.GET.get('filter', 'month')
    labels = None
    data = None
    answers = None
    anwers_per_question = None
    eye_count = None
    image_eye_zone = None

    gender = request.GET.get('gender')
    patient_iin = request.GET.get("iin")

    total_result_queryset = TestResults.objects.filter(test_type_id=test_type_id)
    if gender:
        total_result_queryset = total_result_queryset.filter(iin__gender=gender)
    if patient_iin:
        total_result_queryset = total_result_queryset.filter(iin__iin=patient_iin)

    total_result = total_result_queryset.count()

    test_type = TestTypes.objects.get(id=test_type_id)

    if test_type_id == 2:
        test_name = 'M-CHAT-R'
        mchat_queryset = MChat.objects.all()
        if gender:
            mchat_queryset = mchat_queryset.filter(result_id__iin__gender=gender)
        if patient_iin:
            mchat_queryset = mchat_queryset.filter(result_id__iin__iin=patient_iin)
        test_description = (
            MChatRiskLevel.objects.filter(m_chat__in=mchat_queryset)
            .annotate(count=Count('m_chat'))
            .values('name', 'count')
        )

        labels, data = get_test_stats(filter_type, test_type, gender, patient_iin)
        answers = get_total_anwsers(MChat, gender=gender, patient_iin=patient_iin)
        anwers_per_question = get_total_anwer_per_question(MChat, gender=gender, patient_iin=patient_iin)

    elif test_type_id == 1:
        test_name = 'Eye Tracking'
        test_description = get_test_description(EyeDescription, 'eye_tracking', gender=gender, patient_iin=patient_iin)
        labels, data = get_test_stats(filter_type, test_type, gender, patient_iin)
        eye_count = get_eyecount_stats(gender=gender, patient_iin=patient_iin)
        image_eye_zone = get_eye_zone_sums_by_image(gender=gender, patient_iin=patient_iin)

    elif test_type_id == 3:
        test_name = 'SCQ'
        test_description = get_test_description(SCQDescriptions, 'scq', gender=gender, patient_iin=patient_iin)
        labels, data = get_test_stats(filter_type, test_type, gender, patient_iin)
        answers = get_total_anwsers(SCQ, gender=gender, patient_iin=patient_iin)
        anwers_per_question = get_total_anwer_per_question(SCQ, gender=gender, patient_iin=patient_iin)

    elif test_type_id == 4:
        test_name = 'CARS'
        test_description = get_test_description(CarsDescriptions, 'cars', gender=gender, patient_iin=patient_iin)
        labels, data = get_test_stats(filter_type, test_type, gender, patient_iin)
        answers = get_total_anwsers(Cars, CarsAnswers, 'cars', gender=gender, patient_iin=patient_iin)
        anwers_per_question = get_total_anwer_per_question(Cars, test_type_id, gender=gender, patient_iin=patient_iin)

    elif test_type_id == 5:
        test_name = 'ATEC'
        test_description = get_test_description(AtecDescriptions, 'atec', gender=gender, patient_iin=patient_iin)
        labels, data = get_test_stats(filter_type, test_type, gender, patient_iin)
        answers = get_total_anwsers(Atec, AtecAnswers, 'atec', gender=gender, patient_iin=patient_iin)
        anwers_per_question = get_total_anwer_per_question(Atec, test_type_id, gender=gender, patient_iin=patient_iin)
    
    elif test_type_id == 6:
        test_name = 'CASD'
        test_description = get_test_description(CasdDescriptions, 'casd', gender=gender, patient_iin=patient_iin)
        labels, data = get_test_stats(filter_type, test_type, gender, patient_iin)
        answers = get_total_anwsers(Casd, CasdAnswers, 'casd', gender=gender, patient_iin=patient_iin)
        anwers_per_question = get_total_anwer_per_question(Casd, test_type_id, gender=gender, patient_iin=patient_iin)

    context = {
        'code': 'standard_tests_analysis',
        'title': 'Тест бойынша аналитикалық талдау',
        'test_types': test_types,
        'test_type_id': test_type_id,
        'total_result': total_result,
        'test_description': test_description,
        'labels': labels,
        'data': data,
        'filter_type': filter_type,
        'answers': answers,
        'test_name': test_name,
        'anwers_per_question': anwers_per_question,
        'eye_count': eye_count,
        'image_eye_zone': image_eye_zone,
        'gender': gender,
        'patient_iin': patient_iin,
    }

    return render(request, 'analytics/base_analysis.html', context)


def general_analysis(request):
    test_types = TestTypes.objects.all()

    total_users = User.objects.filter(role=1).count()
    total_male = User.objects.filter(role=1,gender=1).count
    total_female = User.objects.filter(role=1,gender=2).count
    average_age = calculate_average_age_from_db()
    average_point_m_chat = round(MChat.objects.aggregate(Avg('score'))['score__avg'],3)
    average_point_atec = round(Atec.objects.aggregate(Avg('score'))['score__avg'],3)
    average_point_scq = round(SCQ.objects.aggregate(Avg('score'))['score__avg'],3)
    average_point_cars = round(Cars.objects.aggregate(Avg('score'))['score__avg'],3)
    average_point_casd = round(Casd.objects.aggregate(Avg('score'))['score__avg'],3)
    total_test = TestResults.objects.count()

    total_eye = TestResults.objects.filter(test_type_id=1).count()
    total_m_chat = TestResults.objects.filter(test_type_id=2).count()
    total_scq = TestResults.objects.filter(test_type_id=3).count()
    total_cars = TestResults.objects.filter(test_type_id=4).count()
    total_atec = TestResults.objects.filter(test_type_id=5).count()
    total_casd = TestResults.objects.filter(test_type_id=6).count()

    statistics_all = {
        'M-CHAT-R': get_desc_statistics(MChat),
        'ATEC': get_desc_statistics(Atec),
        'CARS': get_desc_statistics(Cars),
        'SCQ': get_desc_statistics(SCQ),
        'CASD':get_desc_statistics(Casd),
    }

    stat_labels = {
        'total': 'Барлығы',
        'unique': 'Уникалды мәндер',
        'mean': 'Орташа мәні',
        'minimum': 'Минимум',
        'maximum': 'Максимум',
        'std_dev': 'Стандартты ауытқу',
        'variance': 'Дисперсия',
    }

    context = {
        'code':'general_analysis',
        'title': 'Аналитика по тестам',
        'total_users': total_users,
        'total_male': total_male,
        'total_female': total_female,
        'average_age': average_age,
        'average_point_m_chat':average_point_m_chat,
        'average_point_atec':average_point_atec,
        'average_point_scq':average_point_scq,
        'average_point_cars':average_point_cars,
        'average_point_casd':average_point_casd,
        'total_test':total_test,
        'total_m_chat':total_m_chat,
        'total_atec':total_atec,
        'total_scq':total_scq,
        'total_cars':total_cars,
        'total_eye':total_eye,
        'total_casd':total_casd,
        'statistics_all':statistics_all,
        'stat_labels': stat_labels,
        'test_types':test_types,
    }

    return render(request, 'analytics/base_analysis.html', context)
