import re

import requests
from bs4 import BeautifulSoup

from tasks.models import Task


def parse_habr_vacancies(pages=5):
    """Парсит вакансии с Habr Career и сохраняет в Task"""

    base_url = "https://career.habr.com/vacancies"
    created_count = 0

    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        print(f"\n--- Страница {page} ---")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка запроса страницы {page}: {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        vacancy_cards = soup.find_all("div", class_="vacancy-card")

        if not vacancy_cards:
            print(f"Страница {page} пуста, завершаем")
            break

        print(f"Найдено вакансий: {len(vacancy_cards)}")

        for card in vacancy_cards:
            title_tag = card.find("a", class_="vacancy-card__title-link")
            if not title_tag:
                print("❌ Нет тега с заголовком")
                continue

            title = title_tag.get_text(strip=True)
            link = title_tag.get("href")
            print(f"✅ Заголовок: {title}")
            print(f" Ссылка: {link}")

            source_id = None
            if link:
                match = re.search(r"/vacancies/(\d+)", link)
                source_id = match.group(1) if match else None
                print(f" source_id: {source_id}")

            if not source_id:
                print(f"Не удалось извлечь ID из ссылки: {link}")
                continue

            full_url = f"https://career.habr.com{link}"

            desc_tag = card.find("div", class_="vacancy-card__description")
            description = desc_tag.get_text(strip=True) if desc_tag else ""

            description = re.sub(r"\s+", " ", description)
            description = description.strip()

            salary_pattern = r"(\d[\d\s]*\d)\s*(?:₽|руб|рублей|₽/мес)"
            salary_match = re.search(salary_pattern, description + " " + title, re.IGNORECASE)
            salary = salary_match.group(1) if salary_match else None

            if salary:
                print(f" Зарплата: {salary}")

            exists = Task.objects.filter(source="habr", source_id=source_id).exists()

            if exists:
                print(f"Пропущено (дубликат): {title}")
                continue

            Task.objects.create(
                title=title, description=description, url=full_url, source="habr", source_id=source_id, status="new"
            )
            created_count += 1
            print(f"Сохранено: {title}")

    print(f"Всего создано новых задач с Habr: {created_count}")
    return created_count
