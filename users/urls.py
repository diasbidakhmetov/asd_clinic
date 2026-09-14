from django.urls import path
from users.views import login, register, profile, logout, all_results,test_card,staff_register

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('staff_register/', staff_register, name='staff_register'),
    path('profile/', profile, name='profile'),
    path('profile/<str:user_id>/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    path('all_results/', all_results, name='all_results'),
    path('all_results/<str:user_id>/', all_results, name='all_results'),
    path('test_type/<int:test_type_id>/', all_results, name='test_types'),
    path('test_type/<int:test_type_id>/<str:user_id>/', all_results, name='test_types'),
    
    path('test_type/<int:test_type_id>/page/<int:page>/', all_results, name='filtered_paginator'),
    
    path('page/<int:page>/', all_results, name='paginator'),
    path('test_card/', test_card, name='test_card'),
    path('test_card/<str:user_id>/', test_card, name='test_card'),
]