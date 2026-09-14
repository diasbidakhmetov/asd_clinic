from django.db.models import Avg, Count, Max, Min, StdDev, Variance
from django.db.models.functions import Cast
from django.db import models


def avg_of_avg(grouped_scores):
    avg_scores = [item['avg_score'] for item in grouped_scores if item['avg_score'] is not None]

    if avg_scores:
        overall_avg = sum(avg_scores) / len(avg_scores)
        print(f"Среднее из средних: {overall_avg}")
    else:
        print("Нет данных")

def get_desc_statistics(Table):
    stats = Table.objects.aggregate(
        total=Count('result_id', distinct=True),
        unique=Count('score', distinct=True),
        mean=Avg(Cast('score', models.FloatField())),
        minimum=Min(Cast('score', models.FloatField())),
        maximum=Max(Cast('score', models.FloatField())),
        std_dev=StdDev(Cast('score', models.FloatField())),
        variance=Variance(Cast('score', models.FloatField())),
    )
    return stats
