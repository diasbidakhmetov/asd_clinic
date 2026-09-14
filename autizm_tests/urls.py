from django.urls import path
from autizm_tests.views import (
    tests,eye_tracking_result, submit_mchat, save_gaze_data, train_model,
    save_model, load_model, save_screen_size, submit_scq,save_cars_results,save_atec_results,
    test_guide,temp_test_results,casd_result_submit
)

app_name = 'autizm_tests'

urlpatterns = [
    path('tests/<str:code_name>', tests, name='tests'),
    path('submit_mchat/', submit_mchat, name='submit_mchat'),
    path('eye_tracking_result/', eye_tracking_result, name='eye_tracking_result'),
    path('save_gaze_data/', save_gaze_data, name='save_gaze_data'),
    path('train_model/', train_model, name='train_model'),
    path("save_model/", save_model, name="save_model"),
    path("load_model/", load_model, name="load_model"),
    path("save_screen_size/", save_screen_size, name="save_screen_size"),
    path('submit_scq/', submit_scq, name='submit_scq'),
    path("save_cars_results/", save_cars_results, name="save_cars_results"),
    path('save_atec_results/', save_atec_results, name='save_atec_results'),
    path('test_guide/<str:code_name>', test_guide, name='test_guide'),
    path('temp_test_results',temp_test_results,name="temp_test_results"),
    path('casd_result_submit/', casd_result_submit, name='casd_result_submit'),

]
