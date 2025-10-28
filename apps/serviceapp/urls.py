from django.urls import path
from . import views
from .utils import get_quote_request

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('career/', views.career, name='career'),

    path('quote-request/', views.quete_request, name='quote_request'),
    path('job-application/<int:vacancy_id>/', views.job_application, name='job_application'),

    #  Use slug instead of pk for dynamic services
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),


    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('contact/', views.contact, name='contact'),
    path("api/unread-count/", views.unread_count_api, name="unread_count_api"),

]
