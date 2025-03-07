from django.contrib import admin
from accounts.models import CustomUser
from bot.admin import AudioRequestInline
from django.contrib import admin
import os
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.contrib import messages
from .models import GoogleDriveCredentials
from utils.google_drive import upload_to_drive, get_drive_service, find_folder_by_date, create_folder
from google_auth_oauthlib.flow import InstalledAppFlow
import tempfile
import datetime

admin.site.site_header = "SURRAT Admin Panel"
admin.site.site_title = "SURRAT Admin"
admin.site.index_title = "Welcome to SURRAT Admin"

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [AudioRequestInline]
    list_display = ('email',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'email', 'first_name', 'last_name')
    readonly_fields = ('password', )
    filter_horizontal = ("groups", "user_permissions")  # ✅ Allow permissions to be managed



SCOPES = ['https://www.googleapis.com/auth/drive.file']

@admin.register(GoogleDriveCredentials)
class GoogleDriveCredentialsAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_id', 'refresh_token', 'created_at', 'updated_at')
    fields = ('user', 'client_id', 'client_secret', 'refresh_token', 'access_token', 'token_expiry')
    readonly_fields = ('created_at', 'updated_at')


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # For non-superusers, pre-fill and lock the user field
            if obj is None:  # Adding a new credential
                form.base_fields['user'].initial = request.user
            form.base_fields['user'].disabled = True  # Make it read-only in the form
            # Limit queryset to current user's credentials
            form.base_fields['user'].queryset = CustomUser.objects.filter(id=request.user.id)
        return form

