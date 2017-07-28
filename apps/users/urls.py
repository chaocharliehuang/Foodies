from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^process_signup$', views.process_signup, name='process_signup'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^update_profile$', views.update_profile, name='update_profile'),
    url(r'^unfriend/(?P<id>[0-9]+)/$', views.unfriend, name='unfriend'),
    url(r'^find_friend$', views.find_friend, name='find_friend'),
    url(r'^add_friend/(?P<id>[0-9]+)/$', views.add_friend, name='add_friend'),
    url(r'^display_friends$', views.display_friends, name='display_friends'),
    url(r'^add_friend2group/(?P<id>[0-9]+)/$', views.add_friend2group, name='add_friend2group'),
    url(r'^remove_friend_from_group/(?P<id>[0-9]+)/$', views.remove_friend_from_group, name='remove_friend_from_group'),
    url(r'^suggest_food$', views.suggest_food, name='suggest_food')
]
