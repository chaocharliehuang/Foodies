from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^query_api$', views.query_api, name='query_api'),
    url(r'^query_business/(?P<id>[\w\-]+)/$', views.query_business, name='query_business'),
]
