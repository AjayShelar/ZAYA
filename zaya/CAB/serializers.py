from collections import OrderedDict

from allauth.account.adapter import get_adapter
from django.contrib.auth import authenticate
from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import activate, deactivate
from drf_dynamic_fields import DynamicFieldsMixin
from phonenumber_field.serializerfields import PhoneNumberField

from rest_auth.models import TokenModel
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from django.utils.translation import ugettext_lazy as _
from .models import User, UserProfile, Cab, Ride, Route, Location


class UserDataSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    photo = serializers.ReadOnlyField()
    name = serializers.CharField(required=True)
    id = serializers.ReadOnlyField()
    is_staff = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        user = User(
            phone_number=validated_data['phone_number'],
            first_name=validated_data['name'])
        user.clean()
        user.save()

        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data['name']
        instance.clean()
        instance.save()

        # Create profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        profile.save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name')


class PhotoUploadSerializer(serializers.Serializer):
    photo = serializers.ImageField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        profile, c = UserProfile.objects.get_or_create(
            user=validated_data['user'])

        profile.photo = validated_data['photo']
        profile.save()
        return profile


class CabSerializer(serializers.Serializer):
    owner = UserDataSerializer()
    cab_type = serializers.CharField(
        source='get_cab_type_display', required=True)
    status = serializers.CharField(source='get_status_display', required=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Cab
        fields = '__all__'


class VRCUploadSerializer(serializers.Serializer):
    vrc = serializers.FileField()
    Cab = serializers.StringRelatedField()

    def create(self, validated_data):
        c = Cab.objects.get(id=validated_data['cab'])
        c.vrc = validated_data['vrc']
        c.save()
        return c


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class RideSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display', required=True)
    status = serializers.CharField(source='get_status_display', required=True)
    route = RouteSerializer()
    cab = CabSerializer()
    passenger = UserDataSerializer(many=True, required=True)

    driver = UserDataSerializer()

    class Meta:
        model = Ride
        fields = '__all__'
