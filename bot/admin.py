import os
import tempfile
import datetime
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html
from bot.models import AudioRequest, instruction_per_page, RequestCounter, ArchivedAudioRequest
from utils.google_drive import upload_to_drive, get_drive_service, create_folder, \
    get_last_file_number, find_folder_by_date, find_surrat_folder


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



# def export_to_google_drive(modeladmin, request, queryset):
#     try:
#         file_ids = []
#         base_id = 10000  # Starting ID
#
#         # Get the Drive service once
#         service = get_drive_service(request.user)
#
#         # Get today's date (e.g., "2025-03-04")
#         today_date = datetime.datetime.now().strftime("%Y-%m-%d")
#
#         # Search for an existing folder with today's date
#         folder_id = find_folder_by_date(service, today_date)
#
#         # If no folder exists, create one with just the date
#         if not folder_id:
#             folder_id = create_folder(service, today_date)
#
#         # Process each object
#         for index, obj in enumerate(queryset):
#             current_id = base_id + index  # Increment ID for each object (10000, 10001, etc.)
#
#             # Handle the text file with UTF-8 encoding
#             if obj.transcribed_text:
#                 with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt',
#                                                  encoding='utf-8-sig') as temp_text_file:
#                     temp_text_file.write(obj.transcribed_text)
#                     temp_text_path = temp_text_file.name
#
#                 # Verify the encoding locally
#                 with open(temp_text_path, 'rb') as f:
#                     raw_content = f.read()
#                     print(f"Raw bytes for {current_id}.txt: {raw_content}")
#                     # Expected UTF-8 for "moadde nie manná": b'moadde nie mann\xc3\xa1'
#
#                 text_file_name = f"{current_id}.txt"
#                 text_file_id = upload_to_drive(request.user, temp_text_path, text_file_name, folder_id)
#                 file_ids.append(text_file_id)
#                 os.unlink(temp_text_path)
#
#             # Handle the audio file
#             if obj.audio:
#                 audio_path = obj.audio.path  # Assumes audio is a FileField with a local path
#                 if os.path.exists(audio_path):
#                     audio_file_name = f"{current_id}.mp3"
#                     audio_file_id = upload_to_drive(request.user, audio_path, audio_file_name, folder_id)
#                     file_ids.append(audio_file_id)
#                 else:
#                     print(f"Audio file not found at: {audio_path}")
#     except Exception as e:
#         modeladmin.message_user(request, f"Export failed: {str(e)}", level=messages.ERROR)
#         return None
#     else:
#         modeladmin.message_user(request, f"{len(file_ids)} file(s) successfully exported to Google Drive.",
#                                 level=messages.SUCCESS)
#     return None
#     # # return HttpResponse(f"Data exported to Google Drive with file IDs: {', '.join(file_ids)}")
#     # # Show a success message in the admin interface
#     # message = f"{len(file_ids)} file(s) successfully exported to Google Drive."
#     # modeladmin.message_user(request, message, level=messages.SUCCESS)
#     # return None  # Return None to stay on the same page
#
#
# export_to_google_drive.short_description = "Export to Google Drive"


# This is the final and perfect worked
# def export_to_google_drive(modeladmin, request, queryset):
#     try:
#         file_ids = []
#
#         # Get the Drive service
#         service = get_drive_service(request.user)
#
#         # Ensure 'Surrat data' folder exists
#         folder_id = find_surrat_folder(service)
#         if not folder_id:
#             folder_id = create_folder(service, "Surrat data")  # Always use this name
#
#         # Get the last file number in the 'Surrat data' folder
#         last_number = get_last_file_number(service, folder_id)
#         next_number = last_number + 1  # Start naming from the next number
#
#         # Process each object
#         for obj in queryset:
#             current_id = next_number  # Assign current file number
#             next_number += 1  # Increment for next file
#
#             # Handle the text file
#             if obj.transcribed_text:
#                 with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8-sig') as temp_text_file:
#                     temp_text_file.write(obj.transcribed_text)
#                     temp_text_path = temp_text_file.name
#
#                 text_file_name = f"{current_id}.txt"
#                 text_file_id = upload_to_drive(request.user, temp_text_path, text_file_name, folder_id)
#                 file_ids.append(text_file_id)
#                 os.unlink(temp_text_path)
#
#             # Handle the audio file
#             if obj.audio:
#                 audio_path = obj.audio.path  # Assumes audio is a FileField with a local path
#                 if os.path.exists(audio_path):
#                     audio_file_name = f"{current_id}.mp3"
#                     audio_file_id = upload_to_drive(request.user, audio_path, audio_file_name, folder_id)
#                     file_ids.append(audio_file_id)
#
#     except Exception as e:
#         modeladmin.message_user(request, f"Export failed: {str(e)}", level=messages.ERROR)
#         return None
#     else:
#         modeladmin.message_user(request, f"{len(file_ids)} file(s) successfully exported to Google Drive.",
#                                 level=messages.SUCCESS)
#     return None


def export_to_google_drive(modeladmin, request, queryset=None, obj_id=None):
    """
    Export selected queryset or a single object to Google Drive.
    If obj_id is provided, export only that object; otherwise, use queryset.
    """
    try:
        file_ids = []

        # Get the Drive service
        service = get_drive_service(request.user)

        # Ensure 'Surrat data' folder exists
        folder_id = find_surrat_folder(service)
        if not folder_id:
            folder_id = create_folder(service, "Surrat data")

        # Get the last file number in the 'Surrat data' folder
        last_number = get_last_file_number(service, folder_id)
        next_number = last_number + 1 if last_number is not None else 10000

        # Determine objects to process
        if obj_id:  # Single object from detail page
            obj = ArchivedAudioRequest.objects.get(id=obj_id)
            objects_to_process = [obj]
        else:  # Queryset from action
            objects_to_process = queryset

        # Process each object
        for obj in objects_to_process:
            current_id = next_number
            next_number += 1

            # Handle the text file
            if obj.transcribed_text:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8-sig') as temp_text_file:
                    temp_text_file.write(obj.transcribed_text)
                    temp_text_path = temp_text_file.name

                text_file_name = f"{current_id}.txt"
                text_file_id = upload_to_drive(request.user, temp_text_path, text_file_name, folder_id)
                file_ids.append(text_file_id)
                os.unlink(temp_text_path)

            # Handle the audio file
            if obj.audio:
                audio_path = obj.audio.path
                if os.path.exists(audio_path):
                    audio_file_name = f"{current_id}.mp3"
                    audio_file_id = upload_to_drive(request.user, audio_path, audio_file_name, folder_id)
                    file_ids.append(audio_file_id)

    except Exception as e:
        modeladmin.message_user(request, f"Export failed: {str(e)}", level=messages.ERROR)
        return None if not obj_id else HttpResponseRedirect(reverse('admin:bot_archivedaudiorequest_change', args=[obj_id]))
    else:
        modeladmin.message_user(request, f"{len(file_ids)} file(s) successfully exported to Google Drive.",
                                level=messages.SUCCESS)
        return None if not obj_id else HttpResponseRedirect(reverse('admin:bot_archivedaudiorequest_change', args=[obj_id]))

export_to_google_drive.short_description = "Export to Google Drive"


@admin.register(ArchivedAudioRequest)
class ArchivedAudioRequestAdmin(admin.ModelAdmin):
    fields = ("id", "audio", "transcribed_text", "created_at")
    readonly_fields = ("id", "audio", "created_at")
    actions = [export_to_google_drive]
    # Custom template
    change_form_template = "admin/bot/archivedaudiorequest/change_form.html"
    def export_single_to_google_drive(self, request, obj_id):
        """View to handle export from the detail page."""
        return export_to_google_drive(self, request, obj_id=obj_id)

    def response_change(self, request, obj):
        """Handle form submission and redirect to export if '_save_and_export' is clicked."""
        if "_save_and_export" in request.POST:
            # Save the object first
            self.save_model(request, obj, self.get_form(request, obj), change=True)
            # Redirect to the export view
            return HttpResponseRedirect(reverse('admin:bot_archivedaudiorequest_export', args=[obj.pk]))
        return super().response_change(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:obj_id>/export/', self.admin_site.admin_view(self.export_single_to_google_drive),
                 name='bot_archivedaudiorequest_export'),
        ]
        return custom_urls + urls




