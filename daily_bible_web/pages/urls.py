from django.urls import path
from . import views

urlpatterns = [
    path("", views.daily_page, name="home"),
    path("<slug:page_date>/", views.daily_page, name="daily_page"),
]