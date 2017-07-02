from django.conf.urls import url

from .views import sign_up, home

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^signup/$', sign_up, name='signup'),
]