from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from phonenumber_field.modelfields import PhoneNumberField


class UserType(object):
    DRIVER = 'd'
    OWNER = 'o'
    PASSENGER = 'p'

    CHOICES = [(DRIVER, 'DRIVER'), (OWNER, 'OWNER'), (PASSENGER, 'PASSENGER')]


class CustomUserManager(UserManager):
    def create_superuser(self, username, phone_number, password, **kwargs):
        extra_fields = {'is_active': True, 'phone_number': phone_number}
        return super(CustomUserManager, self).create_superuser(
            username, None, password, **extra_fields)


class User(AbstractUser):
    phone_number = PhoneNumberField(unique=True)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'User', blank=True, null=True, related_name='created_users')
    edited_by = models.ForeignKey('User', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    pan_card = models.FileField(
        upload_to=None, blank=True, null=True, max_length=500)
    license = models.FileField(
        upload_to=None, blank=True, null=True, max_length=500)
    type = models.CharField(
        choices=UserType.CHOICES, default='p', max_length=64)

    REQUIRED_FIELDS = ('phone_number', )
    objects = CustomUserManager()


# Create your models here.
class CabType(object):
    SUV = 'v'
    SEDAN = 's'
    MINIVAN = 'm'
    OTHER = 'o'

    CHOICES = [(SUV, 'SUV, seats up to 6 riders'),
               (SEDAN, 'SEDAN, seats up to 4 riders'),
               (MINIVAN, 'MINIVAN, seats up to 4 riders'), (OTHER, 'Other')]


class CabStatus(object):
    BOOKED = 'b'
    UNAVAILABLE = 'u'
    AVAILABLE = 'a'

    CHOICES = [(BOOKED, 'already booked'),
               (UNAVAILABLE, 'temporary unavailable'),
               (AVAILABLE, 'available for booking')]


class Cab(models.Model):
    cab_number = models.CharField(
        max_length=255, unique=True, blank=False, null=False)
    # Certificate of Registration of vehicle
    vrc = models.FileField(
        upload_to=None, max_length=500, blank=True, null=True)
    cab_type = models.CharField(
        max_length=255,
        choices=CabType.CHOICES,
        unique=True,
        blank=False,
        null=False)
    status = models.CharField(max_length=65, choices=CabStatus.CHOICES)
    owner = models.OneToOneField(
        User, related_name="cabs", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cab_number)


class LocationType(object):
    SOURCE = 's'
    DESTINATION = 'd'

    CHOICES = [
        (SOURCE, 'from'),
        (DESTINATION, 'to'),
    ]


class Location(models.Model):
    type = models.CharField(
        max_length=255,
        choices=LocationType.CHOICES,
        unique=True,
        blank=False,
        null=False)
    latitude = models.CharField(
        max_length=255, unique=True, blank=False, null=False)
    longitude = models.CharField(
        max_length=255, unique=True, blank=False, null=False)

    def __str__(self):
        return str(self.latitude) + '==>>' + str(self.longitude)


class Route(models.Model):
    source = models.OneToOneField(
        Location, related_name="routes_source", on_delete=models.CASCADE)

    destination = models.OneToOneField(
        Location, related_name='routes_destination', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.source) + '==>>' + str(self.destination)


class RideStatus(object):
    COMPLETED = 'c'
    IN_PROGRESS = 'i'
    BOOKED = 'b'
    CANCELED_BY_USER = 'c_u'
    CANCELED_BY_DRIVER = 'c_d'

    CHOICES = [
        (COMPLETED, 'COMPLETED'),
        (BOOKED, 'BOOKED'),
        (CANCELED_BY_USER, 'CANCELED_BY_USER'),
        (CANCELED_BY_DRIVER, 'CANCELED BY DRIVERER'),
        (IN_PROGRESS, 'IN PROGRESS'),
    ]


class Ride(models.Model):
    route = models.OneToOneField(
        Route, related_name="rides_routes", on_delete=models.CASCADE)

    status = models.CharField(
        max_length=255,
        choices=RideStatus.CHOICES,
        unique=True,
        blank=False,
        null=False)
    cab = models.OneToOneField(
        Cab, related_name="rides_cab", on_delete=models.CASCADE)

    passenger = models.ForeignKey(
        'User', related_name='rides_passengers', on_delete=models.CASCADE)

    driver = models.OneToOneField(
        User, related_name="rides_dirvers", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cab) + '==>>' + str(self.driver) + '==>>' + str(
            self.route)
