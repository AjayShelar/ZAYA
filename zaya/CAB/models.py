from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError, ObjectDoesNotExist


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

    type = models.CharField(
        choices=UserType.CHOICES, default='p', max_length=64)

    REQUIRED_FIELDS = ('phone_number', )
    objects = CustomUserManager()

    def clean(self):
        if not self.username:
            # Set username as phone number
            self.username = str(self.phone_number)

        if not self.password:
            self.set_unusable_password()

    @staticmethod
    def create_user(**kwargs):
        user = User(**kwargs)
        user.clean()
        user.save()
        return user

    @property
    def name_prop(self):
        return self.name()

    def name(self):
        return str(self.first_name + " " + self.last_name).strip()

    def photo(self):
        try:
            return self.profile.photo.url
        except Exception as e:
            return None

    def __str__(self):
        return str(self.name() or self.phone_number.__str__())


def photo_file_name(instance, filename):
    return "user_photo" + str(instance.user.pk)


def pan_card_file_name(instance, filename):
    return "user_pan_card" + str(instance.user.pk)


def license_file_name(instance, filename):
    return "user_license" + str(instance.user.pk)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile')
    photo = models.ImageField(upload_to=photo_file_name, null=True, blank=True)
    pan_card = models.FileField(
        upload_to=pan_card_file_name, blank=True, null=True, max_length=500)
    license = models.FileField(
        upload_to=license_file_name, blank=True, null=True, max_length=500)


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
    AVAILABLE_FOR_SHARING = 'a_s'
    AVAILABLE_FOR_SINGLE = 'a_s'

    CHOICES = [
        (BOOKED, 'already booked'),
        (UNAVAILABLE, 'temporary unavailable'),
        (AVAILABLE_FOR_SHARING, 'available for booking for share'),
        (AVAILABLE_FOR_SINGLE, 'available for booking for single'),
    ]


def vrc_file_name(instance, filename):
    return "cab_vrc" + str(instance.owner.pk)


class Cab(models.Model):
    cab_number = models.CharField(
        max_length=255, unique=True, blank=False, null=False)
    # Certificate of Registration of vehicle
    vrc = models.FileField(
        upload_to=vrc_file_name, max_length=500, blank=True, null=True)
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
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return '(' + str(self.latitude) + ',' + str(self.longitude) + ')'


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


class RideType(object):
    SHARING = 's'
    NO_SHARING = 'n'

    CHOICES = [(SHARING, 'SHARING'), (NO_SHARING, 'NOT SHARING')]


class Ride(models.Model):
    route = models.OneToOneField(
        Route, related_name="rides_routes", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=255,
        choices=RideType.CHOICES,
        unique=True,
        blank=False,
        null=False)
    status = models.CharField(
        max_length=255,
        choices=RideStatus.CHOICES,
        unique=True,
        blank=False,
        null=False)
    cab = models.OneToOneField(
        Cab, related_name="rides_cab", on_delete=models.CASCADE)
    passenger = models.ManyToManyField("User", related_name="rides_passengers")

    driver = models.OneToOneField(
        User, related_name="rides_dirvers", on_delete=models.CASCADE)

    def clean(self):
        if not self.driver.type in ['d', 'o']:
            raise ValidationError('selected user is not owner or driver')

        if self.cab.status in ['b', 'u']:
            raise ValidationError(self.cab.get_status_display())
        if self.cab.status not in ['b', 'u']:
            if self.type == 's':
                if self.cab.status == 'a_s':
                    pass
                else:
                    raise ValidationError(self.cab.get_status_display())
            elif self.type == 'n':
                if self.cab.status == 'n_s':
                    pass
                else:
                    raise ValidationError(self.cab.get_status_display())

    @staticmethod
    def get_user_rides(user):
        return Ride.objects.filter(passenger=user)

    @staticmethod
    def get_driver_rides(user):
        return Ride.objects.filter(driver=user)

    def __str__(self):
        return str(self.cab) + '==>>' + str(self.route.source) + '==>>' + str(
            self.route.destination)
