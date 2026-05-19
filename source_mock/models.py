from django.db import models
from django.utils import timezone


class MockTask(models.Model):
    """Модель задачи из внешнего источник"""

    title = models.CharField(max_length=255, verbose_name="Заголовок", help_text="Напишите заголовок")
    description = models.TextField(verbose_name="Описание", blank=True, help_text="Напишите описание")
    url = models.URLField(
        verbose_name="Ссылка на оригинал", help_text="Напишите ссылку на оригинал", blank=True, null=True
    )
    published_at = models.DateTimeField(
        verbose_name="Когда опубликована", help_text="Напишите дату публикации", default=timezone.now
    )
    is_processed = models.BooleanField(
        default=False, verbose_name="Обработано/не обработано", help_text="Парсер перенёс задачу в основную таблицу"
    )

    class Meta:
        verbose_name = "Тестовая задача"
        verbose_name_plural = "Тестовые задачи"
        ordering = ["-published_at"]

    def __str__(self):
        return f"[Mock] {self.title}"
