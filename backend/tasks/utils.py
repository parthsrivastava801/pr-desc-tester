"""Utility helpers for task statistics and reporting."""

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone

from .models import Task


def get_task_summary(user: User) -> dict:
    """
    Return a summary of task counts by status for a given user.

    Returns a dict with keys: total, todo, in_progress, done, overdue.
    """
    qs = Task.objects.filter(owner=user)
    now = timezone.now()

    counts = qs.aggregate(
        total=Count('id'),
        todo=Count('id', filter=Q(status=Task.Status.TODO)),
        in_progress=Count('id', filter=Q(status=Task.Status.IN_PROGRESS)),
        done=Count('id', filter=Q(status=Task.Status.DONE)),
        overdue=Count(
            'id',
            filter=Q(due_date__lt=now) & ~Q(status=Task.Status.DONE),
        ),
    )
    return counts


def get_priority_breakdown(user: User) -> list[dict]:
    """
    Return task counts per priority level for a given user.

    Returns a list of dicts: [{'priority': <label>, 'count': <int>}, ...]
    ordered from highest to lowest priority.
    """
    qs = (
        Task.objects.filter(owner=user)
        .values('priority')
        .annotate(count=Count('id'))
        .order_by('-priority')
    )

    label_map = {v: label for v, label in Task.Priority.choices}
    return [
        {'priority': label_map.get(row['priority'], str(row['priority'])), 'count': row['count']}
        for row in qs
    ]


def get_overdue_tasks(user: User):
    """Return a queryset of overdue tasks for the given user."""
    now = timezone.now()
    return (
        Task.objects.filter(owner=user, due_date__lt=now)
        .exclude(status=Task.Status.DONE)
        .select_related('owner')
        .prefetch_related('tags')
        .order_by('due_date')
    )


def bulk_update_status(task_ids: list[int], new_status: str, user: User) -> int:
    """
    Bulk-update the status of multiple tasks owned by *user*.

    Returns the number of tasks actually updated.
    Only tasks owned by the given user are modified (ownership guard).
    """
    valid_statuses = [choice[0] for choice in Task.Status.choices]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status '{new_status}'. Must be one of {valid_statuses}.")

    updated = Task.objects.filter(id__in=task_ids, owner=user).update(status=new_status)
    return updated
