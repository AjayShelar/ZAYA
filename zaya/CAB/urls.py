from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from .views import *
urlpatterns = [
    # r'^api/v1/user/((?P<pk>[0-9]+)/)?$', UserView.as_view()
]
