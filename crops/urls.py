from django.urls import path
from crops.views import index, fertilization, upload_pdf_to_s3, recommend_fertilizers, get_crops_by_group, generate_table, generate_recommendations, save_plant_analysis 


urlpatterns = [
    # path("", fertilization, name="fertilization"),
    path('', index, name='index'),
    path("upload-pdf", upload_pdf_to_s3, name="upload-pdf"),
    path("recommend-fertilizers/", recommend_fertilizers, name="recommend-fertilizers"),
    path('get-crops/', get_crops_by_group, name='get_crops_by_group'),

    path('generate-table/', generate_table, name='generate_analysis_table'),
    path('generate-recommendations/', generate_recommendations, name='generate_recommendations'),

    path('save-plant-analysis/', save_plant_analysis, name='save_plant_analysis'),
]
