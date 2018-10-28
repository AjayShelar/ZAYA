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
from .models import User, UserProfile, Cab, Ride, Route


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


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        user = authenticate(
            username=username, password=password, phone_number=phone_number)

        if user:
            if not user.is_active:
                msg = 'User account is disabled.'
                raise exceptions.ValidationError(msg)
        else:
            msg = 'Unable to log in with provided credentials.'
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


class PhotoUploadSerializer(serializers.Serializer):
    photo = serializers.ImageField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        profile, c = UserProfile.objects.get_or_create(
            user=validated_data['user'])

        profile.photo = validated_data['photo']
        profile.save()
        return profile


# FarmMappingSerializer(read_only=True)
# class Rideserializer(serializers.ModelSerializer):
#     passenger = UserDataSerializer(many=True, required=True)
#     driver = UserDataSerializer(many=False, required=True)
#     cab = serializers.CharField(required=True)
#     district = serializers.CharField(required=True)
#     taluka = serializers.CharField(required=True)
#     village = serializers.CharField(required=True)

#     class Meta(object):
#         model = Farm
#         fields = [
#             'area', 'area_unit', 'owner', 'state', 'district', 'taluka',
#             'village', 'farm_supervisors', 'id', 'mapping'
#         ]

#     def create(self, validated_data):
#         state, c = IndiaState.objects.get_or_create(
#             name=validated_data.pop('state'))
#         district, c = IndiaDistrict.objects.get_or_create(
#             name=validated_data.pop('district'), state=state)
#         taluka, c = IndiaTaluka.objects.get_or_create(
#             name=validated_data.pop('taluka'), district=district)
#         village, c = IndiaVillage.objects.get_or_create(
#             name=validated_data.pop('village'), taluka=taluka)

#         validated_data['india_state'] = state
#         validated_data['india_district'] = district
#         validated_data['india_taluka'] = taluka
#         validated_data['india_village'] = village

#         farm_supervisors_validated = validated_data.pop('farm_supervisors')
#         # Update the  instance
#         instance = super(FarmSerializer, self).create(validated_data)

#         farm_supervisors = []
#         for farm_supervisor_validated in farm_supervisors_validated:
#             user = User.objects.get(
#                 phone_number=farm_supervisor_validated['phone_number'])
#             farm_supervisors.append(user)

#         # Update M2M field
#         for supervisor in farm_supervisors:
#             instance.farm_supervisors.add(supervisor)

#         return instance

#     def update(self, instance, validated_data):
#         print(validated_data)
#         state, c = IndiaState.objects.get_or_create(
#             name=validated_data.pop('state'))
#         district, c = IndiaDistrict.objects.get_or_create(
#             name=validated_data.pop('district'), state=state)
#         taluka, c = IndiaTaluka.objects.get_or_create(
#             name=validated_data.pop('taluka'), district=district)
#         village, c = IndiaVillage.objects.get_or_create(
#             name=validated_data.pop('village'), taluka=taluka)

#         validated_data['india_state'] = state
#         validated_data['india_district'] = district
#         validated_data['india_taluka'] = taluka
#         validated_data['india_village'] = village

#         farm_supervisors_validated = validated_data.pop('farm_supervisors')
#         farm_supervisors = []
#         for farm_supervisor_validated in farm_supervisors_validated:
#             user = User.objects.get(
#                 phone_number=farm_supervisor_validated['phone_number'])
#             farm_supervisors.append(user)

#         for supervisor in instance.farm_supervisors.all():
#             if not supervisor in farm_supervisors:
#                 instance.farm_supervisors.remove(supervisor)

#         # Update M2M field
#         for supervisor in farm_supervisors:
#             instance.farm_supervisors.add(supervisor)

#         # Update the  instance
#         instance = super(FarmSerializer, self).update(instance, validated_data)

#         return instance
