from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.db.models import DateTimeField, Q, Count
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime
from django.utils.translation import activate, deactivate
from django.views.decorators.csrf import csrf_exempt
from phonenumbers import PhoneNumber
from rest_framework import permissions, routers, viewsets, generics, mixins
from rest_framework.decorators import list_route, api_view
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, GenericAPIView, UpdateAPIView, \
    RetrieveUpdateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, SAFE_METHODS, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import rest_framework as filters
import rest_framework.filters
from .models import User, UserProfile, Cab, Ride, Route, Location
from .serializers import UserDataSerializer, UserSerializer, PhotoUploadSerializer, CabSerializer, \
RideSerializer, VRCUploadSerializer, RouteSerializer, LocationSerializer
from django.http import HttpResponse, Http404, JsonResponse


class IsAdminUserOrReadOnly(IsAdminUser):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        is_admin = super(IsAdminUserOrReadOnly, self).has_permission(
            request, view)

        return (request.user and request.user.is_authenticated and request.method in SAFE_METHODS)\
               or is_admin


def get_object_or_exception(queryset, model, *args, **kwargs):
    # First get the object from the QS.
    # If the Object is not in QS, it is possible that the object still exists but the user does not have permissions
    #
    # This might be more inefficient because Queryset here might use some JOINs which are slow.
    try:
        return queryset.get(*args, **kwargs)
    except ObjectDoesNotExist:
        # Check if the object exists in the model
        try:
            model.objects.get(*args, **kwargs)
            raise PermissionDenied()
        except ObjectDoesNotExist:
            raise Http404()


def user_qs(user):
    if user.is_staff:
        return User.objects.all()
    return User.objects.filter(id=user.id)


# Create your views here.
class UserView(RetrieveAPIView, CreateAPIView, generics.UpdateAPIView,
               ListAPIView):
    permission_classes = (IsAdminUserOrReadOnly, )

    queryset = User.objects.all()
    serializer_class = UserDataSerializer

    def get_queryset(self):
        return user_qs(self.request.user)

    def get_object(self):
        if self.request.query_params.get('phone_number', None):
            return get_object_or_exception(
                self.get_queryset(),
                User,
                phone_number='+' +
                self.request.query_params.get('phone_number'))

        return get_object_or_exception(
            self.get_queryset(), User, id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk', None) and not request.query_params.get(
                'phone_number', None):
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)


class PhotoUploadView(CreateAPIView):
    permission_classes = (IsAdminUserOrReadOnly, )

    queryset = UserProfile.objects.all()
    serializer_class = PhotoUploadSerializer
    parser_classes = (
        MultiPartParser,
        FormParser,
    )


class CabView(ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView):

    permission_classes = (IsAdminUserOrReadOnly, )
    serializer_class = CabSerializer

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk', None):
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return Cab.objects.all()


class VRCUploadView(CreateAPIView):
    permission_classes = (IsAdminUserOrReadOnly, )

    queryset = Cab.objects.all()
    serializer_class = VRCUploadSerializer
    parser_classes = (
        MultiPartParser,
        FormParser,
    )


class LocationView(ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView):

    permission_classes = (IsAdminUserOrReadOnly, )
    serializer_class = LocationSerializer

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk', None):
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return Location.objects.all()


class RouteView(ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView):

    permission_classes = (IsAdminUserOrReadOnly, )
    serializer_class = RouteSerializer

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk', None):
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return Route.objects.all()


class RideView(ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView):

    permission_classes = (IsAdminUserOrReadOnly, )
    serializer_class = RideSerializer

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk', None):
            return self.list(request, *args, **kwargs)
        else:
            return self.retrieve(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.GET.get('user', None):
            user = User.objects.get(id=self.request.GET.get('user'))
            print(user)
            return Ride.get_user_rides(user)
        elif self.request.GET.get('driver', None):
            user = User.objects.get(id=self.request.GET.get('driver'))
            print(user)
            return Ride.get_driver_rides(user)

        return Ride.objects.all()


from django.views.generic import TemplateView


class Home(TemplateView):
    template_name = 'home.html'