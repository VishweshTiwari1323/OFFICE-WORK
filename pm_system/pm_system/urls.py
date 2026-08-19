from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import RoleBasedLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication Routes
    path('login/', RoleBasedLoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/login/', RoleBasedLoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Include Core App Routes
    path('', include('core.urls')),
]