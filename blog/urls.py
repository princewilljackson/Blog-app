from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/',views.post_list, name='post_list_by_tag'), # List post(s) by tag
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/',views.post_share, name='post_share'),
]