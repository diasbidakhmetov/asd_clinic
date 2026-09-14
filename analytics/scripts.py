

from django.db.models import Count
from results.models import TestResults,EyeCount

from django.db.models.functions import TruncMonth, TruncDay, TruncYear
from collections import OrderedDict
from datetime import datetime

from django.db.models import Sum, F
from django.db.models.functions import Cast
from django.db.models import IntegerField

from django.db.models import Q
from users.models import User


def get_test_description(Table, code_name, gender=None, patient_iin=None):
    queryset = Table.objects.all()

    if gender:
        queryset = queryset.filter(**{
            f"{code_name}__result_id__iin__gender": gender
        })

    if patient_iin:
        queryset = queryset.filter(**{
            f"{code_name}__result_id__iin__iin": patient_iin
        })

    test_description = (
        queryset
        .annotate(count=Count(code_name))
        .values('name', 'count')
    )

    return test_description


def get_test_stats(group_by='month', test_type=None, gender=None, patient_iin=None):
    if test_type:
        queryset = TestResults.objects.filter(test_type=test_type)

    if gender:
        queryset = queryset.filter(iin__gender=gender)

    if patient_iin:
        queryset = queryset.filter(iin__iin=patient_iin)

    now = datetime.now()
    data_dict = OrderedDict()

    if group_by == 'day':
        queryset = queryset.annotate(period=TruncDay('date_taken'))
        format_str = '%d %b %Y'
    elif group_by == 'year':
        queryset = queryset.annotate(period=TruncYear('date_taken'))
        format_str = '%Y'
    else:
        queryset = queryset.filter(date_taken__year=now.year)
        queryset = queryset.annotate(period=TruncMonth('date_taken'))
        format_str = '%B'

        for month in range(1, 13):
            month_date = datetime(now.year, month, 1)
            data_dict[month_date.strftime(format_str)] = 0

    aggregated = queryset.values('period').annotate(count=Count('id')).order_by('period')

    for entry in aggregated:
        label = entry['period'].strftime(format_str)
        data_dict[label] = entry['count']

    return list(data_dict.keys()), list(data_dict.values())


def get_total_anwsers(Table, AnswerTable=None, code_name=None, gender=None, patient_iin=None):
    if AnswerTable:
        queryset = AnswerTable.objects.all()
        if gender:
            queryset = queryset.filter(**{f"{code_name}__result_id__iin__gender": gender})
        if patient_iin:
            queryset = queryset.filter(**{f"{code_name}__result_id__iin__iin": patient_iin})
        total_answer = (
            queryset
            .annotate(count=Count(code_name))
            .values('name', 'count')
        )
    else:
        queryset = Table.objects.all()
        if gender:
            queryset = queryset.filter(result_id__iin__gender=gender)
        if patient_iin:
            queryset = queryset.filter(result_id__iin__iin=patient_iin)
        total_answer = queryset.values('answer').annotate(count=Count('id'))
    return total_answer


def get_total_anwer_per_question(Table, AnswerTable=None, gender=None, patient_iin=None):
    if AnswerTable:
        queryset = Table.objects.all()
        if gender:
            queryset = queryset.filter(result_id__iin__gender=gender)
        if patient_iin:
            queryset = queryset.filter(result_id__iin__iin=patient_iin)

        results = (
            queryset
            .values('question__name', 'answer__name')
            .annotate(count=Count('id'))
            .order_by('question__name', 'answer__name')
        )
    else:
        queryset = Table.objects.all()
        if gender:
            queryset = queryset.filter(result_id__iin__gender=gender)
        if patient_iin:
            queryset = queryset.filter(result_id__iin__iin=patient_iin)

        results = (
            queryset
            .values('question__name', 'answer')
            .annotate(count=Count('id'))
            .order_by('question__name', 'answer')
        )
    return results


def get_eyecount_stats(gender=None, patient_iin=None):
    queryset = EyeCount.objects.annotate(
        neitral_int=Cast('neitral', IntegerField()),
        social_int=Cast('social', IntegerField())
    )

    if gender:
        queryset = queryset.filter(test_result_id__iin__gender=gender)

    if patient_iin:
        queryset = queryset.filter(test_result_id__iin__iin=patient_iin)

    results = queryset.aggregate(
        total_neitral=Sum('neitral_int'),
        total_social=Sum('social_int')
    )

    total_neitral = results['total_neitral'] or 0
    total_social = results['total_social'] or 0
    total_sum = total_neitral + total_social

    if total_sum > 0:
        percent_neitral = round(total_neitral * 100 / total_sum, 2)
        percent_social = round(total_social * 100 / total_sum, 2)
    else:
        percent_neitral = percent_social = 0.0

    return {
        'total_neitral': total_neitral,
        'total_social': total_social,
        'total_sum': total_sum,
        'percent_neitral': percent_neitral,
        'percent_social': percent_social
    }


def get_eye_zone_sums_by_image(gender=None, patient_iin=None):
    queryset = EyeCount.objects.annotate(
        neitral_int=Cast('neitral', IntegerField()),
        social_int=Cast('social', IntegerField())
    )

    if gender:
        queryset = queryset.filter(test_result_id__iin__gender=gender)

    if patient_iin:
        queryset = queryset.filter(test_result_id__iin__iin=patient_iin)

    results = (
        queryset
        .values('image__id', 'image__number', 'image__image')
        .annotate(
            total_neitral=Sum('neitral_int'),
            total_social=Sum('social_int'),
            total=Sum(F('neitral_int') + F('social_int'))
        )
        .order_by('image__number')
    )

    return list(results)



def get_user_iin(last_name, first_name, father_name=None):
    filters = Q(
        last_name=last_name.strip(),
        first_name=first_name.strip()
    )

    if father_name is None or not father_name.strip():
        filters &= Q(father_name__isnull=True) | Q(father_name__exact="")
    else:
        filters &= Q(father_name=father_name.strip())

    users = User.objects.filter(filters)

    if users.count() == 1:
        return users.first().iin
    elif users.count() > 1:
        return "Найдено несколько пользователей с одинаковыми ФИО"
    else:
        return None
