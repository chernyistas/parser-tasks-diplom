from django.test import TestCase
from django.utils import timezone

from source_mock.models import MockTask


class MockTaskModelTest(TestCase):
    """Тесты для модели MockTask"""

    def test_create_mock_task(self):
        """Создание тестовой задачи"""
        task = MockTask.objects.create(
            title="Тестовая задача", description="Описание", url="https://example.com", published_at=timezone.now()
        )
        self.assertEqual(task.title, "Тестовая задача")
        self.assertFalse(task.is_processed)

    def test_str_method(self):
        """Метод __str__ возвращает конкретную строку"""
        task = MockTask.objects.create(title="Моя задача")
        self.assertEqual(str(task), "[Mock] Моя задача")
