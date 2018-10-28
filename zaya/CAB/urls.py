from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from . import views
urlpatterns = [
    url(r'^api/v1/user/((?P<pk>[0-9]+)/)?$', views.UserView.as_view()),
    url(r'^api/v1/user/photo/$', views.PhotoUploadView.as_view())
]
