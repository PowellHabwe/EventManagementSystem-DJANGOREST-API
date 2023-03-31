from django.urls import path
from . import views



urlpatterns = [
    # PAYMENT ENDPOINTS
    path('access/token', views.getAccessToken, name='get_mpesa_access_token'),
    path('stk', views.lipa_na_mpesa_online, name='stkinfo'),

]