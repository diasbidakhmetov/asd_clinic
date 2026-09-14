from django.urls import path
from results.views import eye_results,test_results

app_name = 'results'

urlpatterns = [
    path('eye_results/',eye_results, name='eye_results'),
    path('results/test_results/<str:test_type>/<int:result_id>/', test_results, name='test_results')

]