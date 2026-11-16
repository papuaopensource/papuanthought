from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils import timezone

User = get_user_model()

USER_FIELDS = {"first_name", "last_name"}


def authenticate_by_email(email: str, password: str, request=None):
    """Sign-in for the site: email + password only (usernames are not accepted)."""
    if not email or not password:
        return None
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        return None
    return authenticate(request, username=user.username, password=password)


def accept_invitation(token: str, email: str, username: str, password: str) -> User:
    from .models import Invitation
    try:
        invitation = Invitation.objects.get(token=token, used_at__isnull=True)
    except Invitation.DoesNotExist:
        raise ValueError("This invitation link is invalid or has already been used.")
    if User.objects.filter(username=username).exists():
        raise ValueError("Username is already taken.")
    if User.objects.filter(email=email).exists():
        raise ValueError("This email is already registered.")
    user = User.objects.create_user(
        username=username, email=email, password=password, is_active=True
    )
    invitation.used_at = timezone.now()
    invitation.save(update_fields=["used_at"])
    send_welcome_email(user)
    return user


def send_welcome_email(user: User) -> None:
    send_mail(
        subject="Welcome to Papuan Thought",
        message=(
            f"Hi {user.first_name or user.username},\n\n"
            "Welcome to Papuan Thought — we're really glad you're here.\n\n"
            "You're now part of a community of writers and thinkers sharing ideas "
            "from Papua and beyond. Here are a few things you can do to get started:\n\n"
            f"  • Complete your profile: /settings/profile/\n"
            f"  • Write your first article: /write/\n"
            f"  • Explore what others have written: /\n\n"
            "We look forward to reading your voice.\n\n"
            "— The Papuan Thought Team"
        ),
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )


def change_password(user, old_password: str, new_password: str) -> bool:
    if not user.check_password(old_password):
        return False
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True


def change_email(user, new_email: str) -> None:
    if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
        raise ValueError("This email is already in use.")
    user.email = new_email
    user.save(update_fields=["email"])


def delete_account(user) -> None:
    user.delete()


def update_profile(user, photo=None, **data) -> "Profile":
    user_dirty = False
    for field in list(data.keys()):
        if field in USER_FIELDS:
            setattr(user, field, data.pop(field))
            user_dirty = True
    if user_dirty:
        user.save(update_fields=list(USER_FIELDS))

    profile = user.profile
    for key, value in data.items():
        setattr(profile, key, value)
    if photo:
        profile.photo = photo
    profile.save()
    return profile
