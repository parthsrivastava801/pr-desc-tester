"""Tests for the tasks API."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Task


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
