from django.db.models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import MyUserManager

# Create your models here.


def validate_mobile(mobile):
    if len((str(mobile))) != 10:
        raise ValidationError("Enter valid mobile number.")
    try:
        int(mobile)
    except:
        raise ValidationError("Enter valid mobile number.")
    return mobile


STATE_CHOICES = [
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttarakhand", "Uttarakhand"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("West Bengal", "West Bengal"),
    ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
    ("Chandigarh", "Chandigarh"),
    ("Dadra and Nagar Haveli and", "Dadra and Nagar Haveli and"),
    ("Daman & Diu", "Daman & Diu"),
    ("Delhi", "Delhi"),
    ("Jammu & Kashmir", "Jammu & Kashmir"),
    ("Ladakh", "Ladakh"),
    ("Lakshadweep", "Lakshadweep"),
    ("Puducherry", "Puducherry")
]

default_profile = "https://storage.googleapis.com/projekt-x-402611.appspot.com/images/profile/default.jpg"


class User(AbstractUser, PermissionsMixin):
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
