from datetime import datetime

from django.db.models import *
import uuid

import Users.models

HOSTEL_CHOICES = [
    ("Day Scholar", "None"),
    ("Aravali", "Aravali"),
    ("Girnar", "Girnar"),
    ("Jwalamukhi", "Jwalamukhi"),
    ("Karakoram", "Karakoram"),
    ("Kumaon", "Kumaon"),
    ("Nilgiri", "Nilgiri"),
    ("Shivalik", "Shivalik"),
    ("Satpura", "Satpura"),
    ("Udaigiri", "Udaigiri"),
    ("Vindhyachal", "Vindhyachal"),
    ("Zanskar", "Zanskar"),
    ("Dronagiri", "Dronagiri"),
    ("Saptagiri", "Saptagiri"),
    ("Kailash", "Kailash"),
    ("Himadri", "Himadri"),
    ("Sahyadri", "Sahyadri"),
    ("Nalanda", "Nalanda")]
BOARDS = [
    ('BRCA', "BRCA"),
    ('BHM', "BHM"),
    ('BSA', 'BSA'),
    ('BSW', 'BSW')
]


def upload_path(instance, filename):
    ext = filename.split(".")[0]
    filename = f'{uuid.uuid4()}.{ext}'
    return f'Database/Club/logo/{filename}'

# Create your models here.


class Club(Model):
    name = CharField(max_length=50, unique=True)
    board = CharField(max_length=50, choices=BOARDS, default="BRCA")
    logo = CharField(max_length=500,
                      default='Database/Club/logo/default.jpg')

    def __str__(self):
        return self.name


class Hostel(Model):
    name = CharField(max_length=50, unique=True)

    def residents(self):
        return Users.models.Profile.objects.filter(hostel=self).count()

    def __str__(self):
        return str(self.name)


class College(Model):
    college_name = CharField(max_length=200)
    college_city = CharField(max_length=100)
    college_state = CharField(max_length=100)
    
    class Meta:
        unique_together= ('college_name','college_city','college_state')


    def __str__(self) -> str:
        return f"{self.college_name} | {self.college_state}"
