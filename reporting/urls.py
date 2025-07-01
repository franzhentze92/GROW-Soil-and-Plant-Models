from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-crops/', views.get_crops_by_group, name='get_crops_by_group'),
    path('generate-table/', views.generate_table, name='generate_table'),
    path('get-products/', views.get_products, name='get_products'),
    path('calculate-products-cost/', views.calculate_products_cost, name='calculate_products_cost'), 
    path('save-plant-agronomist-report-analysis/', views.save_plant_agronomist_report_analysis, name='save_plant_agronomist_report_analysis'),   
]