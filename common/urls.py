from django.urls import path
from .views import set_cookie_redirect, list_farms, list_paddocks, token_to_user, validate_token

# URL patterns for the common app
urlpatterns = [
    path('set-cookie/', set_cookie_redirect, name='set_cookie_redirect'),

    # User management "gestion" API endpoints
    path('farm-management/list-farms', list_farms, name='list_farms'),
    path('farm-management/list-paddocks', list_paddocks, name='list_paddocks'),
    path('farm-management/token-to-user', token_to_user, name='token_to_user'),
    path('farm-management/validate-token', validate_token, name='validate_token'),
]