from django.urls import path
from . import views

app_name = "journal"

urlpatterns = [
    path("", views.journal_home, name="home"),
    path("delete/<int:pk>/", views.delete_note, name="delete_note"),
    path("toggle-pin/<int:pk>/", views.toggle_pin, name="toggle_pin"),
]
