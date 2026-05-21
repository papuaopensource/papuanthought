from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email")


@admin.register(Profile)
class ProfileAdmin(ModelAdmin):
    list_display = ("user", "location", "created_at")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)
