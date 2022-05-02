from django.urls import path
from django.conf import settings

from . import views


urlpatterns = [
	#Leave as empty string for base url
	path('', views.index, name="index"),
	path('telegram/', views.telegram, name="telegram"),
]
