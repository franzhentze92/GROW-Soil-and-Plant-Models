from django.urls import path
from .views import index, generate_table, generate_recommendations, save_soil_analysis, tolerance_test

urlpatterns = [
    path('', index, name='soil_analysis'),
    path('generate-table/', generate_table, name='generate_soil_table'),
    path('generate-recommendations/', generate_recommendations, name='generate_soil_recommendations'),
    path('save-soil-analysis/', save_soil_analysis, name='save_soil_analysis'),
    path('tolerance-test/', tolerance_test, name='tolerance_test'),
] 