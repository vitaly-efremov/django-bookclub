# 📚 Книжный клуб — учебный Django-проект

Проект для занятия по **отладке и профилированию Django-приложений**.

## Быстрый старт

### 1. Установить зависимости
```bash
poetry install
```

### 2. Создать базу данных PostgreSQL
```bash
createdb bookclub
```

### 3. Применить миграции
```bash
poetry run python manage.py migrate
```

### 4. Наполнить БД тестовыми данными
```bash
poetry run python manage.py seed
```

### 5. Запустить сервер
```bash
poetry run python manage.py runserver
```

Открыть: http://127.0.0.1:8000  
Admin: http://127.0.0.1:8000/admin (логин: `admin`, пароль: `admin123`)

### 6. Запустить тесты
```bash
poetry run pytest -v
```

---

## Структура проекта

```
bookclub/
├── bookclub/          # Настройки Django
│   ├── settings.py
│   └── urls.py
├── clubs/             # Основное приложение
│   ├── models.py      # Модели: Genre, Book, Member, Review, ReadingList
│   ├── views.py       # Представления (с намеренными N+1 проблемами!)
│   ├── admin.py       # Настройки Django Admin
│   ├── urls.py        # URL-маршруты
│   └── tests.py       # Тесты
├── templates/         # HTML-шаблоны
├── manage.py
├── pyproject.toml
└── poetry.lock
```

---

## 🐛 Намеренные проблемы производительности

Для демонстрации на занятии в коде оставлены проблемные места:

| Где | Проблема | Как исправить |
|-----|----------|---------------|
| `views.py: index()` | N+1: `book.genre` без `select_related` | `Book.objects.select_related('genre')` |
| `views.py: review_list()` | N+1: нет `select_related` для `member__user` и `book` | `Review.objects.select_related('member__user', 'book')` |
| `views.py: api_books()` | N+1 в цикле + поиск без индекса | `select_related` + `db_index=True` на поле `title` |
| `models.py: average_rating()` | Подсчёт в Python вместо SQL | `annotate(avg=Avg('reviews__rating'))` |
| `views.py: member_profile()` | N+1: `entry.book` без `select_related` | `ReadingList.objects.select_related('book')` |

---

## Инструменты профилирования

**Django Debug Toolbar** — панель справа на каждой странице:
- Вкладка **SQL** — все запросы к БД, время выполнения, дубли
- Вкладка **Time** — время рендеринга
- Вкладка **Templates** — какие шаблоны использовались

