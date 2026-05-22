from source_mock.models import MockTask
from tasks.models import Task


def parse_mock_source():
    """Переносит задачи из MockTask в Task, избегая дублей."""
    unprocessed_tasks = MockTask.objects.filter(is_processed=False)

    print(f"Найдено необработанных задач: {unprocessed_tasks.count()}")

    created_count = 0
    for mock_task in unprocessed_tasks:
        exists = Task.objects.filter(source="mock", source_id=str(mock_task.id)).exists()

        if not exists:
            Task.objects.create(
                title=mock_task.title,
                description=mock_task.description,
                url=mock_task.url,
                source="mock",
                source_id=str(mock_task.id),
                published_at=mock_task.published_at,
                status="new",
            )
            created_count += 1

        mock_task.is_processed = True
        mock_task.save()

    print(f"Создано новых задач: {created_count}")
    return created_count
