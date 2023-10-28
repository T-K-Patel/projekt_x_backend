from datetime import datetime
from django.core.exceptions import ValidationError
from django.db.models import *
from Database.models import Hostel, Club
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as GTL
import uuid


def upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'Users/Profile/profile_photo/{filename}'

def get_superadmim():
    return User.objects.filter(is_superuser=True).first()


def mobile_validator(mobile):
    if len((str(mobile))) != 10:
        raise ValidationError("Enter valid mobile number.")
    try:
        int(mobile)
    except:
        raise ValidationError("Enter valid mobile number.")
    return mobile


def validate_image_size(image):
    # Define the maximum file size in bytes (e.g., 1 MB)
    max_size = 1024 * 1024  # 1 MB

    if image.size > max_size:
        raise ValidationError(
            GTL('The image file size should not exceed 1 MB.'),
            code='invalid_image_size'
        )
    return image


class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    name = CharField(max_length=50)
    email = EmailField(max_length=50, unique=True)
    mobile = BigIntegerField(validators=[mobile_validator], unique=True)
    hostel = ForeignKey(Hostel, on_delete=CASCADE)
    room = CharField(max_length=8)
    state = CharField(max_length=25)
    profile_photo = ImageField(upload_to=upload_path, validators=[
                               validate_image_size], default='Users/Profile/profile_photo/default.jpg')
    isRep = BooleanField(default=False)
    isSecy = BooleanField(default=False)
    isVerified = BooleanField(default=False)
    otp = CharField(max_length=6, null=True, blank=True)
    club = ForeignKey(Club, default=None, on_delete=SET_NULL,
                      null=True, blank=True)
    attended_events = ManyToManyField(
        "Workshops.Workshop", related_name="participants", blank=True)
    points = IntegerField(default=0)
    registered_by = ForeignKey(
        "Users.Profile", on_delete=SET_NULL,null=True,blank=True)
    registered_on = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(condition=Q(isSecy=True), fields=[
                             'club'], name='One Secretory for one club'),
            UniqueConstraint(condition=Q(isRep=True), fields=[
                             'hostel', 'club'], name="One Representative of club for one hostel")
        ]

    def entry(self):
        return self.user.username

    def clean(self):
        if self.isRep and self.isSecy:
            raise ValidationError(
                "Person cannot be Representative and Secretory simultaneously.")
        if (self.isRep or self.isSecy) and not self.club:
            raise ValidationError("Specify Club for " +
                                  ("Secy" if self.isSecy else "Rep"))
        if self.club and not (self.isRep or self.isSecy):
            raise ValidationError("Cannot define club for User")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username


class Query(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    subject = CharField(max_length=150)
    message = TextField(max_length=1000)
    isSolved = BooleanField(default=False)
    date_created = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'subject')

    def __str__(self) -> str:
        return f"{self.user.username}: {self.subject}"
