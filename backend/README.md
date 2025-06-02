# Сервис RAG с использованием OpenRouter

Этот проект реализует сервис Retrieval Augmented Generation (RAG), который позволяет загружать документы (PDF, DOCX, MD), обрабатывать их, сохранять содержимое в векторной базе данных и затем выполнять запросы к большой языковой модели (LLM) через OpenRouter, используя загруженные документы в качестве контекста.

## Возможности

* **Загрузка файлов:** Эндпоинт для загрузки и обработки файлов PDF, DOCX и Markdown.
* **Извлечение и разбиение текста:** Извлекает текст из файлов и разбивает его на удобные фрагменты.
* **Векторные представления:** Генерирует эмбеддинги для фрагментов текста с помощью Sentence Transformers.
* **Векторное хранилище:** Использует FAISS для эффективного поиска по сходству.
* **Интеграция с LLM:** Выполняет запрос к LLM через OpenRouter, предоставляя релевантный контекст из документов.
* **Указание источников:** Возвращает ответ модели вместе с конкретными использованными фрагментами документов.
* **Модульная архитектура:** Код организован по логическим модулям, каждый со своим README.
* **API-ориентированность:** Используется FastAPI для предоставления эндпоинтов загрузки и запроса.

## Структура проекта

```
rag_service/
├── main.py                 # Инициализация FastAPI-приложения и запуск сервера
├── api/                    # Эндпоинты и схемы API
│   ├── endpoints.py
│   ├── schemas.py
│   └── README.md
├── file_processing/        # Извлечение текста и разбиение на фрагменты
│   ├── extractor.py
│   ├── chunking.py
│   └── README.md
├── vector_store/           # Управление эмбеддингами и поиском
│   ├── store.py
│   └── README.md
├── llm_interface/          # Взаимодействие с LLM через OpenRouter
│   ├── openrouter_client.py
│   └── README.md
├── core/                   # Конфигурация и общие утилиты
│   ├── config.py
│   └── README.md
├── storage/                # Папка для загружаемых файлов (создаётся автоматически)
│   └── uploads/
├── .env.example            # Пример файла переменных окружения
├── requirements.txt        # Зависимости Python
└── README.md               # Этот файл
```

## Установка и настройка

1. **Клонировать репозиторий (или создать файлы вручную):**

   ```bash
   # Если используете git:
   # git clone <repository_url>
   # cd rag_service
   ```

2. **Создать и активировать виртуальное окружение:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   ```

3. **Установить зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Настроить переменные окружения:**
   Скопируйте `.env.example` в новый файл `.env` и укажите свои значения:

   ```
   OPENROUTER_API_KEY="your_openrouter_api_key_here"
   # Список моделей: https://openrouter.ai/docs#models
   # Примеры: "mistralai/mistral-7b-instruct" или "openai/gpt-3.5-turbo"
   OPENROUTER_MODEL_NAME="mistralai/mistral-7b-instruct"
   EMBEDDING_MODEL_NAME="all-MiniLM-L6-v2"
   ```

   Замените `"your_openrouter_api_key_here"` на свой реальный ключ API от OpenRouter.

## Запуск сервиса

1. **Запустить сервер FastAPI:**

   ```bash
   uvicorn main:app --reload
   ```

   По умолчанию сервер запускается по адресу `http://127.0.0.1:8000`.

## API-эндпоинты

Документация API (Swagger UI) доступна по адресу: `http://127.0.0.1:8000/docs`.

1. **Загрузка файла:**

   * **Эндпоинт:** `POST /upload`
   * **Формат запроса:** `multipart/form-data` с файлом.
   * **Ответ:** Сообщение с подтверждением.
   * **Пример cURL:**

     ```bash
     curl -X POST -F "file=@/path/to/your/document.pdf" http://127.0.0.1:8000/api/v1/upload
     ```

2. **Запрос к LLM:**

   * **Эндпоинт:** `POST /query`
   * **Тело запроса (JSON):**

     ```json
     {
       "query_text": "What is the main topic of the document?"
     }
     ```
   * **Ответ (JSON):**

     ```json
     {
       "llm_response": "Основная тема документа...",
       "sources": [
         {
           "document_name": "document.pdf",
           "chunk_id": 0,
           "text_preview": "Документ описывает различные аспекты..."
         },
         // ... другие релевантные фрагменты
       ]
     }
     ```
   * **Пример cURL:**

     ```bash
     curl -X POST -H "Content-Type: application/json" \
          -d '{"query_text": "What are the key findings?"}' \
          http://127.0.0.1:8000/api/v1/query
     ```

## Модули

Каждый модуль содержит свой `README.md` в соответствующей папке, описывающий архитектуру и назначение:

* `api/README.md`
* `core/README.md`
* `file_processing/README.md`
* `llm_interface/README.md`
* `vector_store/README.md`

## Примечания

* Векторное хранилище (FAISS-индекс и метаданные документов) пока хранится в памяти. Для сохранения между перезапусками сервера потребуется реализовать загрузку/сохранение индекса и карты документов на диск.
* Папка `storage/uploads` используется для временного хранения загруженных файлов.
* Убедитесь, что у вашего OpenRouter API-ключа достаточно кредитов, и выбранная модель подходит для вашей задачи.
