from django.urls import path
from . import views

app_name = "feeds"

urlpatterns = [
    path("", views.feed_list, name="feed_list"),
    path("refresh/<slug:slug>/", views.refresh_source, name="refresh_source"),
    path("refresh-all/", views.refresh_all, name="refresh_all"),
    path("<int:pk>/", views.feed_detail, name="feed_detail"),
]
