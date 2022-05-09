from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('view_target_list/', views.view_target_list, name='view_target_list'),
    path('load_new_target/', views.load_new_target, name='load_new_target'),
    path('admin/', views.admin, name='admin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('', views.load_new_target, name='load_new_target'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)