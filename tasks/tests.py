from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task


class TaskModelTest(TestCase):
    """Тесты для модели Task"""

    def test_create_task_with_new_status(self):
        """Создание задачи со статусом 'new'"""
        task = Task.objects.create(
            title="Новая задача",
            description="Описание",
            source="mock",
            source_id="123",
            published_at=timezone.now(),
            status="new",
        )
        self.assertEqual(task.status, "new")
        self.assertEqual(str(task), "Новая задача [новая]")

    def test_unique_together_constraint(self):
        """Нельзя создать дубликат с одинаковыми source и source_id"""
        Task.objects.create(title="Задача 2", source="mock", source_id="123")
        with self.assertRaises(IntegrityError):
            Task.objects.create(title="Задача 2", source="mock", source_id="123")


class TaskAPITest(APITestCase):
    """Тесты для API задач"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.client.force_authenticate(user=self.user)
        self.task1 = Task.objects.create(title="API Задача 1", source="mock", source_id="1", status="new")
        self.task2 = Task.objects.create(title="API Задача 2", source="habr", source_id="2", status="in_progress")
        self.url = reverse("tasks:task-list")

    def test_list_tasks(self):
        """GET /api/tasks/ возвращает список задач"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_filter_by_status_new(self):
        """Фильтрация задач по статусу"""
        response = self.client.get(self.url, {"status": "new"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "API Задача 1")

    def test_filter_by_source_habr(self):
        """Фильтрация задач по источнику 'habr'"""
        response = self.client.get(self.url, {"source": "habr"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["source"], "habr")

    def test_create_task(self):
        """POST /api/tasks/ создаем новую задачу"""
        data = {
            "title": "Новая из теста",
            "description": "Тестовое описание",
            "source": "test",
            "source_id": "999",
            "status": "new",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
