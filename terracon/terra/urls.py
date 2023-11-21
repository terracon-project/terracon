from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),  # 뷰 함수와 URL 패턴을 연결
]
