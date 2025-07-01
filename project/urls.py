"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import index_view

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', index_view, name="index"),
    path('plant-analysis/',include('crops.urls')),
    path('soil-analysis/', include('soil_analysis.urls')),
    path('report-generation/', include('reporting.urls')),
    path('api/', include('common.urls')),
    path('analysis-submissions/', include('analysis_submissions.urls')),
    path('analysis-analytics/', include('analysis_analytics.urls')),
]

# Add static files serving for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)