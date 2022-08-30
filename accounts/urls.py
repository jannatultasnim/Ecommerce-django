from django.urls import path
from . import views
urlpatterns = [
   path('register/',views.Register, name='register'),
   path('login/',views.Login, name='login'),
   path('logout/',views.logout, name='logout'),
   path('activate/<uidb64>/<token>',views.activate, name='activate'),
   path('dashboard/',views.Dashboard,name='dashboard'),
   path('forgot_password/',views.forgot_password,name='forgot_password'),
   path('reset_password_validate/<uidb64>/<token>',views.reset_password_validate, name='reset_password_validate'),
   path('reset_password/',views.reset_password,name='reset_password')
   
   
]