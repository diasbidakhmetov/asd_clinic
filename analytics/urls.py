from django.urls import path
from analytics.views import patients,general_analysis,standard_tests_analysis,search_users

app_name = 'analytics'

urlpatterns = [
    path('patients/', patients, name='patients'),

    path('page/<int:page>/', patients, name='paginator'),

    path('search-users/', search_users, name='search_users'),

    path('general_analysis/', general_analysis, name='general_analysis'),
    path('standard_tests_analysis/', standard_tests_analysis, name='standard_tests_analysis'),
    path('test_type/<int:test_type_id>/', standard_tests_analysis, name='test_types'),
]
