from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

USER_FIELDS = {"first_name", "last_name"}


def authenticate_user(credential: str, password: str, request=None):
    return authenticate(request, username=credential, password=password)


def apply_for_membership(username: str, email: str, password: str, motivation: str) -> User:
    if User.objects.filter(username=username).exists():
        raise ValueError("Username is already taken.")
    if User.objects.filter(email=email).exists():
        raise ValueError("Email is already registered.")
    user = User.objects.create_user(
        username=username, email=email, password=password, is_active=False
    )
    user.profile.motivation = motivation
    user.profile.save(update_fields=["motivation"])
    return user


def approve_user(user: User, request=None) -> User:
    user.is_active = True
    user.save(update_fields=["is_active"])
    if request:
        login_url = request.build_absolute_uri(reverse("accounts:login"))
    else:
        login_url = "/accounts/login/"
    send_mail(
        subject="Your account has been approved — Papuan Thought",
        message=(
            f"Hi {user.username},\n\n"
            "Your application to join Papuan Thought has been approved.\n"
            f"You can now sign in and start writing at: {login_url}\n\n"
            "— The Papuan Thought Team"
        ),
        from_email=None,
        recipient_list=[user.email],
        fail_silently=True,
    )
    return user


def create_invitation(email: str, invited_by: User, request) -> "Invitation":
    from .models import Invitation
    if User.objects.filter(email=email).exists():
        raise ValueError("This email is already registered as an account.")
    invitation, created = Invitation.objects.get_or_create(
        email=email,
        defaults={"invited_by": invited_by},
    )
    if not created and invitation.is_used:
        raise ValueError("The invitation for this email has already been used.")
    accept_url = request.build_absolute_uri(
        reverse("accounts:invitation_accept", kwargs={"token": invitation.token})
    )
    send_mail(
        subject="You're invited to join Papuan Thought",
        message=(
            f"Hi,\n\n"
            f"You've been invited by {invited_by.username} to join Papuan Thought, "
            "a community writing platform for Papuans.\n\n"
            f"Click the link below to create your account:\n{accept_url}\n\n"
            "This link can only be used once.\n\n"
            "— The Papuan Thought Team"
        ),
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )
    return invitation


def accept_invitation(token: str, username: str, password: str) -> User:
    from .models import Invitation
    try:
        invitation = Invitation.objects.get(token=token, used_at__isnull=True)
    except Invitation.DoesNotExist:
        raise ValueError("This invitation link is invalid or has already been used.")
    if User.objects.filter(username=username).exists():
        raise ValueError("Username is already taken.")
    if User.objects.filter(email=invitation.email).exists():
        raise ValueError("This email is already registered.")
    user = User.objects.create_user(
        username=username, email=invitation.email, password=password, is_active=True
    )
    invitation.used_at = timezone.now()
    invitation.save(update_fields=["used_at"])
    return user


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
