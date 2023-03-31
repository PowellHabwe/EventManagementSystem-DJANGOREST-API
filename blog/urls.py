from django.urls import path
from . import views

from .views import (
    BlogPostListView, 
    BlogPostDetailView, 
    BlogPostFeaturedView, 
    BlogPostCategoryView,
    StkCallView,
    TicketCreateView,
    index,
    TicketDetail,
    GetTicket,
    MpesaCodeValid
    # lipa_na_mpesa_online
)

urlpatterns = [
    path('', BlogPostListView.as_view()),
    path('featured', BlogPostFeaturedView.as_view()),
    path('category', BlogPostCategoryView.as_view()),
    path('<slug>', BlogPostDetailView.as_view()),

    # CREATE TICKET
    path('ticket/create', TicketCreateView.as_view()),
    path('ticket/get', GetTicket.as_view()),
    path('ticket/go', MpesaCodeValid.as_view()),
    path('ticket/<str:ticketCode>', TicketDetail.as_view()),

    # PAYMENT ENDPOINTS
    path('access/token', views.getAccessToken, name='get_mpesa_access_token'),
    # path('online/lipa', views.lipa_na_mpesa_online, name='stkinfo'),
    path('online/lipa', StkCallView.as_view(), name='stkinfo'),

    path('c2b/register', views.register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', views.confirmation, name="confirmation"),
    path('c2b/validation', views.validation, name="validation"),
    path('c2b/callback', views.call_back, name="call_back"),

    path('b2c/queue', views.call_back, name="b2cq"),
    path('b2c/result', views.call_back, name="b2cr"),
    # path('b2c/trial', views.b2ctemplate, name="b2ctrial"),
    path('b2c/', views.b2c, name="b2c"),

]