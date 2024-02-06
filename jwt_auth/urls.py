from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/token/', views.CookieTokenObtainPairView.as_view()),
]
