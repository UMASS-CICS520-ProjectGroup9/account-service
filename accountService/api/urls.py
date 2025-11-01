from django.urls import path

from . import views

urlpatterns = [
    path('', views.getAllAccounts),
    path('create/', views.createAccount),
    path('update/', views.updateAccount),
    path('delete/', views.deleteAccount),
]
