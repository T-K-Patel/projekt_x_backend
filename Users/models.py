from django.db.models import *
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import MyUserManager
from .utils import *
import uuid

# Create your models here.


class User(AbstractUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = None
    last_name = None
    name = CharField(max_length=100)
    email = EmailField(max_length=100, unique=True)
    mobile = CharField(max_length=10, unique=True,
                       validators=[validate_mobile])
    dob = DateField(null=True, blank=True)
    state = CharField(max_length=50, choices=STATE_CHOICES)
    profile_photo = CharField(max_length=500, default=default_profile)
    otp = CharField(max_length=6, null=True, blank=True)
    is_verified = BooleanField(
        default=False,
        help_text="Designates weather User is verified.",
        verbose_name="Verification Status"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['name', 'email', 'mobile', 'state']
    objects = MyUserManager()

    class Meta:
        constraints = [UniqueConstraint(
            name="Unique email",
            condition=Q(is_verified=True),
            fields=['email'],
            violation_error_message="Cannot verify multiple user with same email.")
        ]

    def __str__(self):
        return f"{self.username}"


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
