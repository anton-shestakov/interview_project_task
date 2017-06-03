from django.core.exceptions import ValidationError
from posts.models import User


def check_user_exists(email):

    exists = User.objects.filter(email=email).exists()

    if exists:
        raise ValidationError("User with this email already exists", code="user_exists")


def check_username_exists(username):

    exists = User.objects.filter(username=username).exists()

    if exists:
        raise ValidationError("User with this username already exists", code="username_exists")
