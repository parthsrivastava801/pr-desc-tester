"""Tests for the tasks API."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Tag, Task


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------

class TaskModelTest(TestCase):
    """Tests for the Task model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_task(self):
        task = Task.objects.create(
            title='Test Task',
            description='A test task',
            owner=self.user,
        )
        self.assertEqual(str(task), 'Test Task')
        self.assertEqual(task.status, Task.Status.TODO)
        self.assertEqual(task.owner, self.user)

    def test_default_ordering(self):
        Task.objects.create(title='First', owner=self.user)
        Task.objects.create(title='Second', owner=self.user)
        tasks = Task.objects.all()
        self.assertEqual(tasks[0].title, 'Second')

    def test_is_overdue_true(self):
        """A past-due task that is not done should be marked overdue."""
        past = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title='Overdue Task',
            due_date=past,
            status=Task.Status.TODO,
            owner=self.user,
        )
        self.assertTrue(task.is_overdue)

    def test_is_overdue_false_when_done(self):
        """A past-due task that IS done should not be marked overdue."""
        past = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title='Done Late Task',
            due_date=past,
            status=Task.Status.DONE,
            owner=self.user,
        )
        self.assertFalse(task.is_overdue)

    def test_is_overdue_false_future(self):
        """A task with a future due date should not be overdue."""
        future = timezone.now() + timedelta(days=5)
        task = Task.objects.create(
            title='Future Task',
            due_date=future,
            status=Task.Status.TODO,
            owner=self.user,
        )
        self.assertFalse(task.is_overdue)

    def test_is_overdue_false_no_due_date(self):
        """A task with no due date is never overdue."""
        task = Task.objects.create(title='No Due', owner=self.user)
        self.assertFalse(task.is_overdue)

    def test_task_str(self):
        task = Task.objects.create(title='My Task Title', owner=self.user)
        self.assertEqual(str(task), 'My Task Title')

    def test_priority_defaults_to_medium(self):
        task = Task.objects.create(title='Default Priority', owner=self.user)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)


class TagModelTest(TestCase):
    """Tests for the Tag model."""

    def test_create_tag(self):
        tag = Tag.objects.create(name='backend', color='#ff5733')
        self.assertEqual(str(tag), 'backend')
        self.assertEqual(tag.color, '#ff5733')

    def test_default_color(self):
        tag = Tag.objects.create(name='default-color')
        self.assertEqual(tag.color, '#6366f1')

    def test_tag_name_unique(self):
        Tag.objects.create(name='unique-tag')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name='unique-tag')


# ---------------------------------------------------------------------------
# API Tests — Tasks
# ---------------------------------------------------------------------------

class TaskAPITest(TestCase):
    """Tests for the Task API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        response = self.client.post('/api/tasks/', {
            'title': 'New Task',
            'description': 'Task description',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Task')
        self.assertEqual(response.data['owner'], 'apiuser')

    def test_list_tasks(self):
        Task.objects.create(title='Task 1', owner=self.user)
        Task.objects.create(title='Task 2', owner=self.user)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_update_own_task(self):
        task = Task.objects.create(title='My Task', owner=self.user)
        response = self.client.patch(f'/api/tasks/{task.id}/', {
            'status': 'in_progress',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_progress')

    def test_cannot_update_others_task(self):
        task = Task.objects.create(title='Their Task', owner=self.other_user)
        response = self.client.patch(f'/api/tasks/{task.id}/', {
            'title': 'Hijacked',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_status(self):
        Task.objects.create(title='Todo', status='todo', owner=self.user)
        Task.objects.create(title='Done', status='done', owner=self.user)
        response = self.client.get('/api/tasks/?status=done')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Done')

    def test_filter_by_priority(self):
        Task.objects.create(title='Low Pri', priority=Task.Priority.LOW, owner=self.user)
        Task.objects.create(title='High Pri', priority=Task.Priority.HIGH, owner=self.user)
        response = self.client.get('/api/tasks/?priority=3')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'High Pri')

    def test_search_by_title(self):
        Task.objects.create(title='Fix login bug', owner=self.user)
        Task.objects.create(title='Write docs', owner=self.user)
        response = self.client.get('/api/tasks/?search=login')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Fix login bug')

    def test_delete_own_task(self):
        task = Task.objects.create(title='Delete Me', owner=self.user)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_cannot_delete_others_task(self):
        task = Task.objects.create(title='Not Mine', owner=self.other_user)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_single_task(self):
        task = Task.objects.create(title='Single Task', owner=self.user)
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Single Task')
        # Detail view includes 'description' and 'tags' (full serializer)
        self.assertIn('description', response.data)
        self.assertIn('tags', response.data)


# ---------------------------------------------------------------------------
# API Tests — Overdue & My Tasks custom actions
# ---------------------------------------------------------------------------

class OverdueEndpointTest(TestCase):
    """Tests for GET /api/tasks/overdue/."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='overdueuser', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_overdue_returns_only_overdue(self):
        past = timezone.now() - timedelta(days=2)
        future = timezone.now() + timedelta(days=2)
        Task.objects.create(title='Overdue', due_date=past, owner=self.user)
        Task.objects.create(title='Future', due_date=future, owner=self.user)
        Task.objects.create(title='No Due', owner=self.user)

        response = self.client.get('/api/tasks/overdue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [t['title'] for t in response.data]
        self.assertIn('Overdue', titles)
        self.assertNotIn('Future', titles)
        self.assertNotIn('No Due', titles)

    def test_done_tasks_excluded_from_overdue(self):
        past = timezone.now() - timedelta(days=1)
        Task.objects.create(
            title='Done Late',
            due_date=past,
            status=Task.Status.DONE,
            owner=self.user,
        )
        response = self.client.get('/api/tasks/overdue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class MyTasksEndpointTest(TestCase):
    """Tests for GET /api/tasks/my_tasks/."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='myuser', password='testpass123'
        )
        self.other = User.objects.create_user(
            username='othermy', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_my_tasks_only_returns_own(self):
        Task.objects.create(title='Mine', owner=self.user)
        Task.objects.create(title='Theirs', owner=self.other)
        response = self.client.get('/api/tasks/my_tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [t['title'] for t in response.data['results']]
        self.assertIn('Mine', titles)
        self.assertNotIn('Theirs', titles)

    def test_my_tasks_empty_when_none(self):
        response = self.client.get('/api/tasks/my_tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


# ---------------------------------------------------------------------------
# API Tests — Tags
# ---------------------------------------------------------------------------

class TagAPITest(TestCase):
    """Tests for the Tag API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='taguser', password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_tag(self):
        response = self.client.post('/api/tags/', {
            'name': 'frontend',
            'color': '#10b981',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'frontend')

    def test_list_tags(self):
        Tag.objects.create(name='alpha')
        Tag.objects.create(name='beta')
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_unauthenticated_cannot_create_tag(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/tags/', {'name': 'hack'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_tag_assigned_to_task(self):
        tag = Tag.objects.create(name='bug', color='#ef4444')
        response = self.client.post('/api/tasks/', {
            'title': 'Fix Bug',
            'tag_ids': [tag.id],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data['id'])
        self.assertIn(tag, task.tags.all())
