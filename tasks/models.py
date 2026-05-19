from django.db import models
from django.utils import timezone


class Task(models.Model):
    """Модель задачи из любого источника"""

    STATUS_CHOICES = [("new", "новая"), ("in_progress", "в работе"), ("done", "выполнена")]

    title = models.CharField(max_length=255, verbose_name="Заголовок", help_text="Напишите заголовок")
    description = models.TextField(verbose_name="Описание", blank=True, help_text="Напишите описание")
    url = models.URLField(
        verbose_name="Ссылка на оригинал", help_text="Напишите ссылку на оригинал", blank=True, null=True
    )
    source = models.CharField(
        max_length=255, verbose_name="Откуда пришла задача(источник)", help_text="Напишите источник задачи"
    )
    source_id = models.CharField(max_length=200, verbose_name="ID в источнике", blank=True)
    published_at = models.DateTimeField(
        verbose_name="Когда опубликована", help_text="Напишите дату публикации", default=timezone.now
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="new", verbose_name="Статус", help_text="Выберите статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-published_at"]
        unique_together = ["source", "source_id"]

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"
