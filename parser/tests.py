from parser.services import parse_mock_source

from django.test import TestCase

from source_mock.models import MockTask
from tasks.models import Task


class ParserTest(TestCase):
    """Тесты для парсера"""

    def setUp(self):
        """Создаём тестовые данные в MockTask"""
        self.mock1 = MockTask.objects.create(
            title="Парсер Задача 1", description="Описание 1", url="https:///example.com/1", is_processed=False
        )
        self.mock2 = MockTask.objects.create(
            title="Парсер задача 2", description="Описание 2", url="https://example.com/2", is_processed=False
        )

    def test_parse_mock_source_create_tasks(self):
        """Парсер переносит задачи из MockTask в Task"""
        created = parse_mock_source()

        self.assertEqual(created, 2)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(MockTask.objects.filter(is_processed=True).count(), 2)

    def test_parse_mock_source_no_duplicate(self):
        """Повторный запуск парсера не создает дубликаты"""
        parse_mock_source()
        created_again = parse_mock_source()

        self.assertEqual(created_again, 0)
        self.assertEqual(Task.objects.count(), 2)
