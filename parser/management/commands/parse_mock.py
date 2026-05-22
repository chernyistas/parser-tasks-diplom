from parser.services import parse_mock_source

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Парсит задачи из Mock-источника и переносит в Task"

    def handle(self, *args, **options):
        self.stdout.write("Запуск парсера Mock-источника...;")
        created = parse_mock_source()
        self.stdout.write(self.style.SUCCESS(f"Готово! Создано задач: {created}"))
