from django.contrib import admin
from bot.models import AudioRequest


@admin.register(AudioRequest)
class AudioRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "page_number",
        "created_at",
    )


class AudioRequestInline(admin.TabularInline):
    model = AudioRequest
    extra = 0
    readonly_fields = ("id", "page_number", "created_at")


#
#
# class CustomUserAdmin(admin.ModelAdmin):
#     inlines = [ChatHistoryInline]
#
#
# # Re-register the User model with the custom admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
