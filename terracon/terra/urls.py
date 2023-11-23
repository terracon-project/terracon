from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),  # 뷰 함수와 URL 패턴을 연결
    path('region/',views.region,name='region'),
    path('instance/',views.instance,name='instance'),
    path('key/',views.key, name='key'),
    path('home/', views.home, name='home'),  # 뷰 함수와 URL 패턴을 연결
    path('list/',views.list,name='list'),
    path('step1/',views.step1,name='step1'),
    path('step2/',views.step2, name='step2'),
]
