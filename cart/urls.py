from django.urls import path
from . import views
urlpatterns = [
   path('',views.Cart, name='cart'),
]