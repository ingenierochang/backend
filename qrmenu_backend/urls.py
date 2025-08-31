"""
URL configuration for qrmenu_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

from django.contrib import admin
from django.urls import path, include

from apps.users.views import LogoutView, auth_users_me

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.core.urls')),
    
    
    path('api/accounts/', include('apps.users.urls')),

    path("auth/logout/", LogoutView.as_view()),
    path("auth/users/me/", auth_users_me),

    


    
    path('restaurants/', include('apps.restaurants.urls')),
    # path('products/', include('apps.products.urls')),

]
"""
from django.contrib import admin
from django.urls import path, include
from apps.users.views import LogoutView, auth_users_me, login_user

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.core.urls')),
    path('api/accounts/', include('apps.users.urls')),

    # 🔥 Alias para compatibilidad con el frontend
    path("auth/login/", login_user, name="alias_login"),
    path("auth/logout/", LogoutView.as_view(), name="alias_logout"),
    path("auth/users/me/", auth_users_me, name="alias_me"),

    path('restaurants/', include('apps.restaurants.urls')),
]
