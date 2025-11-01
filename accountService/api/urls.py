from django.urls import path

from . import views

urlpatterns = [
    path('', views.getAllAccounts),
    path('get/<str:email>/', views.getAccount),
    path('create/', views.createAccount),
    path('update/', views.updateAccount),
    path('delete/', views.deleteAccount),
]
