import re
from parser.habr_parser import parse_habr_vacancies
from parser.services import parse_mock_source
from unittest.mock import Mock, patch

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


class HabrParserTest(TestCase):
    """Тесты для парсера Habr Career"""

    def setUp(self):
        """Очищаем задачи перед каждым тестом"""
        Task.objects.filter(source="habr").delete()

    def test_regex_extracts_id_from_link(self):
        """Регулярное выражение правильно извлекает ID из ссылки"""
        link = "/vacancies/123456789"
        match = re.search(r"/vacancies/(\d+)", link)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "123456789")

        bad_link = "/vacancies/"
        bad_match = re.search(r"/vacancies/(\d+)", bad_link)
        self.assertIsNone(bad_match)

    def test_clean_description_with_regex(self):
        """Регулярное выражение правильно очищает текст"""
        dirty_text = "Python разработчик\n\n   опыт от 3   лет"
        cleaned = re.sub(r"\s+", " ", dirty_text).strip()
        self.assertEqual(cleaned, "Python разработчик опыт от 3 лет")

        dirty_with_tabs = "Java\tразработчик\t\tMiddle"
        cleaned_tabs = re.sub(r"\s+", " ", dirty_with_tabs).strip()
        self.assertEqual(cleaned_tabs, "Java разработчик Middle")

    def test_salary_pattern_matches_correctly(self):
        """Регулярное выражение для зарплаты находит правильные значения"""
        salary_pattern = r"(\d[\d\s]*\d)\s*(?:₽|руб|рублей|₽/мес)"

        text1 = "Зарплата: 300 000 ₽"
        match1 = re.search(salary_pattern, text1, re.IGNORECASE)
        self.assertIsNotNone(match1)
        self.assertEqual(match1.group(1), "300 000")

        text2 = "до 250000 руб"
        match2 = re.search(salary_pattern, text2, re.IGNORECASE)
        self.assertIsNotNone(match2)
        self.assertEqual(match2.group(1), "250000")

        text3 = "150 000 рублей"
        match3 = re.search(salary_pattern, text3, re.IGNORECASE)
        self.assertIsNotNone(match3)
        self.assertEqual(match3.group(1), "150 000")

        text4 = "требования: опыт работы от 3 лет"
        match4 = re.search(salary_pattern, text4, re.IGNORECASE)
        self.assertIsNone(match4)

    @patch("parser.habr_parser.requests.get")
    def test_parse_habr_vacancies_creates_tasks(self, mock_get):
        """Парсер создает задачи из полученных данных"""

        mock_html = """
        <div class="vacancy-card">
            <a class="vacancy-card__title-link" href="/vacancies/9999991">Python Developer</a>
            <div class="vacancy-card__description">Разработка на Python, Django, PostgreSQL. Зарплата: 200 000 ₽</div>
        </div>
        <div class="vacancy-card">
            <a class="vacancy-card__title-link" href="/vacancies/9999992">Java Developer</a>
            <div class="vacancy-card__description">Разработка на Java, Spring, опыт от 3 лет</div>
        </div>
        """

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()

        mock_get.return_value = mock_response

        created = parse_habr_vacancies(pages=1)

        self.assertEqual(created, 2)
        self.assertEqual(Task.objects.filter(source="habr").count(), 2)

        task1 = Task.objects.get(source_id="9999991")
        self.assertEqual(task1.title, "Python Developer")
        self.assertIn("200 000", task1.description)

        task2 = Task.objects.get(source_id="9999992")
        self.assertEqual(task2.title, "Java Developer")

    @patch("parser.habr_parser.requests.get")
    def test_parse_habr_vacancies_no_duplicates(self, mock_get):
        """Повторный запуск парсера не создаёт дубликаты"""

        mock_html = """
        <div class="vacancy-card">
            <a class="vacancy-card__title-link" href="/vacancies/9999991">Python Developer</a>
            <div class="vacancy-card__description">Описание</div>
        </div>
        """

        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        first_run = parse_habr_vacancies(pages=1)

        second_run = parse_habr_vacancies(pages=1)

        self.assertEqual(first_run, 1)
        self.assertEqual(second_run, 0)
        self.assertEqual(Task.objects.filter(source="habr").count(), 1)
