from parser.habr_parser import parse_habr_vacancies

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Парсит вакансии с Habr Career"

    def handle(self, *args, **options):
        self.stdout.write("Запуск парсера Habr Career...")
        created = parse_habr_vacancies()
        self.stdout.write(self.style.SUCCESS(f"Готово! Создано задач: {created}"))
