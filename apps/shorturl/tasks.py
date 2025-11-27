from celery import shared_task

from .models import AccessLog, ShortUrls


@shared_task
def store_log(short_url_id, **kwargs):
    try:
        short_url_instance = ShortUrls.objects.get(pk=short_url_id)
        AccessLog.objects.create(short_url_id=short_url_instance, **kwargs)
    except ShortUrls.DoesNotExist:
        print(f'Could not find ShortUrls with id={short_url_id} to store access log.')
