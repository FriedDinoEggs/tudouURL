from celery import shared_task

from .models import AccessLog


@shared_task
def add(x, y):
    return x + y


@shared_task
def store_log(instance, **kwargs):
    ip_address = kwargs.get('log_ip_address')
    user_agent = kwargs.get('log_user_agent')
    referer = kwargs.get('log_referer')
    AccessLog.objects.create(instance, ip_address, user_agent, referer)
