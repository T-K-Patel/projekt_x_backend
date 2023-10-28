import uuid

# from Database.models import Hostel, Club
from django.db.models import *
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from Database.models import Club
from Database.models import Hostel
from Users.models import Profile


# Create your models here.
def get_superadmim():
    return Profile.objects.filter(user__is_superuser=True).first()


def upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'Workshops/Workshop/poster/{filename}'


class Workshop(Model):
    title = CharField(max_length=100, unique=True)
    poster = ImageField(upload_to=upload_path,default="images/default.jpg")
    venue = CharField(max_length=50)
    time = DateTimeField()
    description = TextField(max_length=1200)
    duration = CharField(max_length=50, default=None, null=True, blank=True)
    contact_person = CharField(max_length=100)
    club = ForeignKey(Club, on_delete=CASCADE)
    hostel = ManyToManyField(Hostel)
    added_by = ForeignKey(Profile, on_delete=models.SET(get_superadmim))
    date_added = DateTimeField(auto_now_add=True)

    def hostels(self):
        return ", ".join([str(hostel) for hostel in self.hostel.all()])

    def clean(self):
        # if not (self.added_by.isRep or self.added_by.isSecy):
        #     raise ValidationError("You cannot add Workshop")
        # if (self.added_by.isRep or self.added_by.isSecy) and self.added_by.club != self.club:
        #     raise ValidationError("You cannot add Workshop of other club")

        pass

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} | {self.club.name}"
