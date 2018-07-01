"""addon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from chart import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$' ,views.profile , name='profile'),
    #
    url(r'^chart_model/$', views.chart_model, name='chart_model'),
    url(r'^optimization/$', views.optimization, name='optimization'),
    url(r'^sq_integr/$', views.coordinate_descent_optimize, name='sq_integr'),
    url(r'^state-space/$', views.state_space, name='state_space'),
    url(r'^alter_step/$', views.alter_step, name='alter_step'),
    url(r'^alter_step_air/$', views.alter_step_air, name='alter_step_air'),
    url(r'^alter_model_temp/$', views.alter_model_temp, name='alter_model_temp'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

