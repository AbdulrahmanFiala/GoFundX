"""
URL configuration for GoFundX project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'projects.views.custom_404'
handler500 = 'projects.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('go_fund_auth.urls')),
    path('projects/', include('projects.urls')),
    path('accounts/', include('allauth.urls')),
    # path('oauth/', include('social_django.urls', namespace='social')),
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
