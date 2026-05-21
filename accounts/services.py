from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

USER_FIELDS = {"first_name", "last_name"}


def authenticate_user(credential: str, password: str, request=None):
    """Authenticate with either email or username."""
    return authenticate(request, username=credential, password=password)


def register_user(username: str, email: str, password: str) -> User:
    if User.objects.filter(username=username).exists():
        raise ValueError("Username already taken.")
    if User.objects.filter(email=email).exists():
        raise ValueError("Email already registered.")
    user = User.objects.create_user(username=username, email=email, password=password)
    user.profile  # trigger signal to ensure profile exists
    return user


def update_profile(user, photo=None, **data) -> "Profile":
    """Update User fields and Profile fields from a single flat dict."""
    user_dirty = False
    for field in list(data.keys()):
        if field in USER_FIELDS:
            setattr(user, field, data.pop(field))
            user_dirty = True
    if user_dirty:
        user.save(update_fields=list(USER_FIELDS & set(vars(user))))

    profile = user.profile
    for key, value in data.items():
        setattr(profile, key, value)
    if photo:
        profile.photo = photo
    profile.save()
    return profile
