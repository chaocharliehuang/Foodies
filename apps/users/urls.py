from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^process_signup$', views.process_signup, name='process_signup'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^find_friend$', views.find_friend, name='find_friend'),
    url(r'^add_friend/(?P<id>[0-9]+)/$', views.add_friend, name='add_friend'),
]
