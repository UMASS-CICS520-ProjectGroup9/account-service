from django.urls import path

from . import views

urlpatterns = [
    path('account/', views.getAllAccounts),
    path('account/get/<str:email>/', views.getAccount),
    path('account/create/', views.createAccount),
    path('account/update/', views.updateAccount),
    path('account/delete/', views.deleteAccount),
    # path('account/delete_all/', views.deleteAllAccounts),
    path('account/count/', views.countAccounts),
    path('account/count_by_role/<str:role>/', views.countAccountsByRole),
    path('account/created_after/<str:date_str>/', views.getAccountsCreatedAfter),
    path('account/role/<str:role>/', views.getAccountsByRole),
    path('authenticate/', views.authenticateAccount),
    path('change_password/', views.changeAccountPassword),
    path('account/updated_before/<str:date_str>/', views.getAccountsUpdatedBefore),
    path('account/change_role/', views.changeAccountRole),
    path('account/toggle_active/', views.toggleAccountActiveStatus),
]
