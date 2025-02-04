from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from bot.models import AudioRequest, instruction_per_page, RequestCounter


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

class RequestCounterAdmin(admin.ModelAdmin):
    list_display = ('user', 'page_number', 'request_count', 'last_request_at', 'updated_at')  # Fields to display in admin panel
    search_fields = ('user__email', 'page_number')  # Enable searching by user email and page number
    list_filter = ('page_number', 'user')  # Filter options in admin panel

admin.site.register(RequestCounter, RequestCounterAdmin)
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
    list_display = ("page_number", "short_instruction_text", "preview_image")
    list_filter = ("page_number",)
    search_fields = ("page_number", "instruction_text")
    readonly_fields = ("preview_image",)  # Show image preview in admin

    fieldsets = (
        ("Page Information", {"fields": ("page_number",)}),
        ("Instruction Details", {"fields": ("instruction_text", "preview_image", "instruction_image")}),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make `page_number` read-only after creation."""
        if obj:
            return self.readonly_fields + ("page_number",)
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of instructions from admin panel."""
        return False

    def short_instruction_text(self, obj):
        """Show only the first 50 characters of the instruction text."""
        return obj.instruction_text[:50] + "..." if obj.instruction_text else "No Instruction"
    short_instruction_text.short_description = "Instruction Preview"

    def preview_image(self, obj):
        """Display an image preview in the admin list."""
        if obj.instruction_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.instruction_image.url)
        return "No Image"
    preview_image.short_description = "Image Preview"

    # def view_on_site_link(self, obj):
    #     """Add a link to view the object (if applicable)."""
    #     url = reverse("admin:bot_instruction_per_page_change", args=[obj.pk])
    #     return mark_safe(f'<a href="{url}" target="_blank">View</a>')
    # view_on_site_link.short_description = "Admin Link"




# @admin.register(instruction_per_page)
# class InstructionAdmin(admin.ModelAdmin):
#     list_display = ("page_number","instruction_text")
#     list_filter = ("page_number", "instruction_text")
#     search_fields = ("page_number", "instruction_text")
#
#     def get_readonly_fields(self, request, obj=None):
#         # If the object is already saved (i.e., it's being edited), make page_number read-only
#         if obj:
#             return self.readonly_fields + ('page_number',)
#         return self.readonly_fields
#
#     def has_delete_permission(self, request, obj=None):
#         return False
