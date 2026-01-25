# Мониторинг конкурентов — веб и десктоп (PyQt6)

Проект содержит две полноценные версии приложения:
- Веб‑сервер на FastAPI с простым фронтендом (HTML/JS), эндпоинтами анализа текста/изображений и парсинга сайтов.
- Десктопное приложение на PyQt6 (один исполняемый файл `.exe` или папка `onedir`) с тем же функционалом и русским интерфейсом.

## Возможности
- Анализ текста конкурента (LLM, OpenRouter) — выявление сильных/слабых сторон, рекомендаций, оценки дизайна и идеи анимации.
- Анализ изображений (Vision) — описание, маркетинговые инсайты, оценка дизайна, анализ визуального стиля, рекомендации, идея анимации.
- Парсинг сайта (Selenium + Chrome + webdriver_manager) — снятие скриншота, сбор Title/H1/первого абзаца, опциональный LLM‑анализ.
- История запросов (history.json) — последние N результатов.

## Архитектура
- `backend/` — серверная логика:
  - [config.py](file:///c:/Users/Ден/Downloads/pem08-master/backend/config.py) — настройки, загрузка `.env`, логирование.
  - [main.py](file:///c:/Users/Ден/Downloads/pem08-master/backend/main.py) — FastAPI приложение и эндпоинты.
  - `models/` — pydantic‑схемы.
  - `services/` — сервисы: OpenAI/OpenRouter, парсер (Selenium), история.
- `frontend/` — простые статики (HTML/CSS/JS), поднимаются сервером с корня `/`.
- `desktop_app/` — окно PyQt6:
  - [main.py](file:///c:/Users/Ден/Downloads/pem08-master/desktop_app/main.py) — вкладки “Анализ текста”, “Анализ изображения”, “Парсинг сайта”.
- Корневые утилиты:
  - [run.py](file:///c:/Users/Ден/Downloads/pem08-master/run.py) — запуск FastAPI.
  - [launcher.py](file:///c:/Users/Ден/Downloads/pem08-master/launcher.py) — входная точка десктопа.
  - [build.py](file:///c:/Users/Ден/Downloads/pem08-master/build.py) — сборка `.exe` (PyInstaller), исключение лишних модулей и пост‑очистка `dist`.

## Требования
- Windows 10+, Python 3.11+ (проверено на 3.12).
- Google Chrome (для парсинга сайтов).
- Действительный ключ OpenRouter (https://openrouter.ai/keys).

## Установка
1. Создать и активировать окружение:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Скопировать `env.example.txt` в `.env` и заполнить:
   - OPENROUTER_API_KEY=ваш_ключ
   - OPENAI_MODEL, OPENAI_VISION_MODEL (по желанию)
   - API_HOST, API_PORT

## Запуск веб‑версии
```bash
.\venv\Scripts\python run.py
```
- Интерфейс: http://localhost:8000
- Документация: http://localhost:8000/docs

## Запуск десктоп‑версии из исходников
```bash
.\venv\Scripts\python launcher.py
```
- Если есть `.env` рядом с `launcher.py` или в корне, он будет загружен автоматически.
- Для парсинга сайтов должен быть установлен Chrome.

## Сборка десктопного `.exe`
- Режим onedir (папка с файлами, быстрый старт):
  ```bash
  .\venv\Scripts\python build.py
  ```
  Итог: `dist/CompetitorMonitor/CompetitorMonitor.exe`
- Чтобы собрать один файл (onefile), замените флаг `--onedir` на `--onefile` в [build.py](file:///c:/Users/Ден/Downloads/pem08-master/build.py) и снова выполните сборку.  
  Итог: `dist/CompetitorMonitor.exe`

### Что делает сборка
- Явно включает только используемые модули PyQt6 (QtCore/QtGui/QtWidgets).
- Исключает тестовые/примерные/кешевые каталоги и метаданные `*.dist-info`.
- Копирует `.env` в `dist/`, если найден в корне.

## Переменные окружения (.env)
См. пример: [env.example.txt](file:///c:/Users/Ден/Downloads/pem08-master/env.example.txt)
- OPENROUTER_API_KEY — ключ OpenRouter (обязателен для LLM/Vision).
- OPENAI_MODEL — модель текста (по умолчанию `google/gemini-2.5-flash-lite-preview-09-2025`).
- OPENAI_VISION_MODEL — модель для изображений (по умолчанию `google/gemini-3-pro-image-preview`).
- API_HOST, API_PORT — хост/порт FastAPI.

## Публикация на GitHub
Добавьте `.env` в `.gitignore` и используйте `env.example.txt` для документации.

### В репозиторий включить
- Корень:
  - README.md, .gitignore, requirements.txt, env.example.txt
  - [run.py](file:///c:/Users/Ден/Downloads/pem08-master/run.py), [launcher.py](file:///c:/Users/Ден/Downloads/pem08-master/launcher.py), [build.py](file:///c:/Users/Ден/Downloads/pem08-master/build.py)
- `backend/` (весь каталог)
- `frontend/` (весь каталог)
- `desktop_app/` (весь каталог)

### Исключить (не коммитить)
- `venv/`, `.venv/` и любые виртуальные окружения
- `dist/`, `build/` (артефакты сборки)
- Любые `__pycache__/`, `*.pyc`, `*.pyo`
- Файлы конфиденциальных ключей: `.env`
- Тесты/примеры/документы, если появятся: `tests/`, `examples/`, `docs/`
- Файлы спецификации и кешей: `*.spec`, `.cache/`, `.pytest_cache/`, `.ruff_cache/`

## Быстрая проверка
- Запустить веб‑версию: `.\venv\Scripts\python run.py`
- Запустить десктоп: `.\venv\Scripts\python launcher.py`
- Собрать десктоп (onedir): `.\venv\Scripts\python build.py`

## Примечания
- При ошибке 401 (“User not found”) во время LLM‑анализа приложение продолжит работу и отобразит результаты парсинга; проверьте ключ в `.env`.
- Для парсинга нужен установленный Google Chrome. Если сайт защищён от автоматизации, используйте задержки/настройки в [parser_service.py](file:///c:/Users\Ден/Downloads/pem08-master/backend/services/parser_service.py).
