from django.contrib import admin
from accounts.models import CustomUser
from bot.admin import AudioRequestInline


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [AudioRequestInline]
