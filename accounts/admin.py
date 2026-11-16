from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.inlines.admin import StackedInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User, Profile, Invitation


class ProfileInline(StackedInline):
    """Shown as a "Profile" tab on the account page (profiles have no admin page of their own)."""

    model = Profile
    tab = True
    verbose_name = "Profile"
    verbose_name_plural = "Profile"
    can_delete = False
    extra = 0
    max_num = 1
    fields = ("photo", "bio", "location", "website", "twitter", "instagram")


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("username", "email", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff")
    search_fields = ("username", "email")
    inlines = [ProfileInline]


@admin.register(Invitation)
class InvitationAdmin(ModelAdmin):
    list_display = ("note_or_token", "invited_by", "created_at", "is_used_display", "invitation_link")
    readonly_fields = ("invitation_link", "token", "invited_by", "created_at", "used_at")
    fields = ("note", "invitation_link", "token", "invited_by", "created_at", "used_at")
    search_fields = ("note",)

    @admin.display(description="Note / Token")
    def note_or_token(self, obj):
        return obj.note or str(obj.token)[:8] + "…"

    @admin.display(description="Used")
    def is_used_display(self, obj):
        return obj.is_used
    is_used_display.boolean = True

    @admin.display(description="Invite Link")
    def invitation_link(self, obj):
        path = obj.accept_path
        return format_html(
            '<div style="display:flex;align-items:center;gap:8px;">'
            '<code style="font-size:11px;color:#a3a3a3;white-space:nowrap;overflow:hidden;'
            'text-overflow:ellipsis;max-width:260px;" title="{0}">{0}</code>'
            '<button type="button"'
            ' onclick="navigator.clipboard.writeText(window.location.origin+\'{0}\').then(()=>{{this.textContent=\'Copied!\';setTimeout(()=>this.textContent=\'Copy\',1500)}})"'
            ' style="flex-shrink:0;cursor:pointer;font-size:11px;padding:2px 10px;'
            'border:1px solid #404040;border-radius:4px;background:transparent;color:#d4d4d4;">'
            'Copy</button>'
            '</div>',
            path,
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.invited_by = request.user
        super().save_model(request, obj, form, change)
