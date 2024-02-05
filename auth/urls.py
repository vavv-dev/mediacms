from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/token/', views.CookieTokenObtainPairWithView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

