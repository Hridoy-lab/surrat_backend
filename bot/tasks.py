# # bots/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import AudioRequest, ArchivedAudioRequest
import logging

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def archive_and_delete_audio_requests(self):
    try:
        # Get initial counts
        total_requests = AudioRequest.objects.count()
        allowed_requests = AudioRequest.objects.filter(user__allow_data_for_training=True).count()
        not_allowed_requests = AudioRequest.objects.filter(user__allow_data_for_training=False).count()

        logger.info(f"""
        Starting archival process:
        - Total requests: {total_requests}
        - Requests with permission: {allowed_requests}
        - Requests without permission: {not_allowed_requests}
        """)

        # Get only the requests where users have allowed data training
        requests_to_archive = AudioRequest.objects.filter(
            user__allow_data_for_training=True
        ).select_related('user')

        archived_count = 0
        error_count = 0

        # Process each request
        for request in requests_to_archive:
            try:
                # Create archive record
                ArchivedAudioRequest.objects.create(
                    audio=request.audio,
                    response_audio=request.response_audio,
                    transcribed_text=request.transcribed_text,
                    translated_text=request.translated_text,
                    gpt_response=request.gpt_response,
                    translated_response=request.translated_response,
                    created_at=request.created_at
                )

                # Delete original request after successful archiving
                # request.delete()
                archived_count += 1

                # logger.info(f"Successfully archived request ID: {request.id} from user: {request.user.email}")

            except Exception as e:
                error_count += 1
                logger.error(f"Error archiving request ID {request.id}: {str(e)}")

        # Log final results
        logger.info(f"""
        Archival process completed:
        - Total requests processed: {allowed_requests}
        - Successfully archived: {archived_count}
        - Failed to archive: {error_count}
        - Requests not archived (no permission): {not_allowed_requests}
        """)
        AudioRequest.objects.all().delete()
        return {
            'status': 'success',
            'total_requests': total_requests,
            'archived_count': archived_count,
            'error_count': error_count,
            'not_archived_count': not_allowed_requests,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Critical error in archive task: {str(e)}")
        raise self.retry(exc=e)


# @shared_task(
#     bind=True,
#     max_retries=3,
#     default_retry_delay=300
# )
# def archive_and_delete_audio_requests(self):
#     try:
#         logger.info("Starting archive_and_delete_audio_requests task...")
#
#         # Fetch requests to archive
#         requests_to_archive = AudioRequest.objects.filter(
#             user__allow_data_for_training=True
#         ).select_related('user')
#
#         logger.info(f"Found {requests_to_archive.count()} requests to archive.")
#
#         archived_count = 0
#         error_count = 0
#
#         for request in requests_to_archive:
#             try:
#                 logger.info(f"Archiving request ID: {request.id}")
#
#                 # Create an archived request
#                 ArchivedAudioRequest.objects.create(
#                     audio=request.audio,
#                     response_audio=request.response_audio,
#                     transcribed_text=request.transcribed_text,
#                     translated_text=request.translated_text,
#                     gpt_response=request.gpt_response,
#                     translated_response=request.translated_response,
#                 )
#
#                 # Delete the original request
#                 request.delete()
#                 archived_count += 1
#
#                 logger.info(f"Successfully archived request ID: {request.id}")
#
#             except Exception as e:
#                 error_count += 1
#                 logger.error(f"Error archiving request ID {request.id}: {str(e)}", exc_info=True)
#
#         logger.info(f"Archival process completed: {archived_count} archived, {error_count} errors.")
#
#         return {
#             'status': 'success',
#             'archived_count': archived_count,
#             'error_count': error_count,
#             'timestamp': timezone.now().isoformat()
#         }
#
#     except Exception as e:
#         logger.error(f"Critical error in archive task: {str(e)}", exc_info=True)
#         raise self.retry(exc=e)
