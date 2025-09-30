from django.urls import path
from . import views

app_name = "journal"

urlpatterns = [
    path("", views.journal_home, name="home"),
    path("save/", views.save_note, name="save_note"),
    path("get/<int:pk>/", views.get_note, name="get_note"),
    path("delete/<int:pk>/", views.delete_note, name="delete_note"),
    path("toggle-pin/<int:pk>/", views.toggle_pin, name="toggle_pin"),
]
