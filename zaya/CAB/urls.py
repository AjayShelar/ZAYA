from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from . import views
urlpatterns = [
    url(r'^api/v1/user/((?P<pk>[0-9]+)/)?$', views.UserView.as_view()),
    url(r'^api/v1/user/photo/$', views.PhotoUploadView.as_view()),
    url(r'^api/v1/cabs/((?P<pk>[0-9]+)/)?$', views.CabView.as_view()),
    url(r'^api/v1/cabs/vrc/$', views.VRCUploadView.as_view()),
    url(r'^api/v1/ride/((?P<pk>[0-9]+)/)?$', views.RideView.as_view()),
    url(r'^api/v1/route/((?P<pk>[0-9]+)/)?$', views.RouteView.as_view()),
    url(r'^api/v1/location/((?P<pk>[0-9]+)/)?$', views.LocationView.as_view()),
]
