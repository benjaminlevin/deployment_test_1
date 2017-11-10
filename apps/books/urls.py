from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^add$', views.add),
    url(r'^(?P<bid>\d+)$', views.book),
    url(r'^(?P<bid>\d+)/add$', views.add_review),
    url(r'^(?P<bid>\d+)/(?P<rid>\d+)/delete$', views.delete_review),
    url(r'^cleardb$', views.cleardb),  
]