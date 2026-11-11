from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Task
from .services import invalidate_dashboard_stats


@receiver([post_save, post_delete], sender=Task)
def clear_dashboard_cache(sender, instance, **kwargs):
    """Any create / edit / delete / status change makes cached stats stale."""
    invalidate_dashboard_stats(instance.owner_id)
