from django.contrib import admin
from accounts.models import CustomUser
from bot.admin import AudioRequestInline

from django.contrib import admin

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


