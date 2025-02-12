# bots/tasks.py
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
        # Get count before archiving
        initial_count = AudioRequest.objects.count()
        logger.info(f"Starting archival process. Found {initial_count} records to archive.")

        # Get all AudioRequest records
        audio_requests = AudioRequest.objects.all()
        archived_count = 0

        # Archive each record
        for request in audio_requests:
            try:
                ArchivedAudioRequest.objects.create(
                    user=request.user,
                    page_number=request.page_number,
                    audio=request.audio,
                    response_audio=request.response_audio,
                    instruction=request.instruction,
                    transcribed_text=request.transcribed_text,
                    translated_text=request.translated_text,
                    gpt_response=request.gpt_response,
                    translated_response=request.translated_response,
                    created_at=request.created_at,
                )
                archived_count += 1
            except Exception as e:
                logger.error(f"Error archiving request {request.id}: {str(e)}")

        logger.info(f"Archival complete. Archived {archived_count} out of {initial_count} records.")

        return {
            'status': 'success',
            'archived_count': archived_count,
            'total_count': initial_count,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in archive task: {str(e)}")
        raise self.retry(exc=e)
