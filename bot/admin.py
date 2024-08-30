from django.contrib import admin
from bot.models import AudioRequest, instruction_per_page


@admin.register(AudioRequest)
class AudioRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "page_number",
        "created_at",
    )
    readonly_fields = (
    "id", "user", "instruction", "audio", "transcribed_text", "translated_text", "gpt_response", "translated_response", "page_number",
    "created_at")
    list_filter = ("user", "page_number")


class AudioRequestInline(admin.TabularInline):
    model = AudioRequest
    extra = 0
    readonly_fields = ("id", "audio", "instruction", "transcribed_text", "translated_text", "gpt_response", "translated_response", "page_number", "created_at")


#
#
# class CustomUserAdmin(admin.ModelAdmin):
#     inlines = [ChatHistoryInline]
#
#
# # Re-register the User model with the custom admin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
@admin.register(instruction_per_page)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ("page_number","instruction_text")
    list_filter = ("page_number", "instruction_text")
    search_fields = ("page_number", "instruction_text")
