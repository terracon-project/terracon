from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),  # 뷰 함수와 URL 패턴을 연결
    path('main/', views.main, name='main'),
    path('create/', views.create, name='create'),
    path('view/', views.view, name='view'),
    path('instances_view/',views.instances_view,name='instance'),
    path('execute_terraform/',views.)
]
