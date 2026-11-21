
# ElevenLabs Transcriber

Небольшой Python-скрипт для работы с ElevenLabs Speech-to-Text API.

Поддерживает:
- POST — транскрибирование аудиофайлов
- GET — получение транскрипции по ID
- DELETE — удаление транскрипции по ID

## Требования

- Python 3.9+
- API-ключ ElevenLabs

## Установка

Клонируй репозиторий или перейди в папку проекта.

Создай виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Установи зависимости:

```bash
pip install requests python-dotenv
```

Создай файл `.env` в корне проекта:

```env
ELEVENLABS_API_KEY=твой_api_ключ
```

Не публикуй файл `.env` и не добавляй его в Git.

## Использование

### POST — транскрибирование

Отправить аудиофайл на транскрибирование:

```bash
python transcribe.py transcribe audio.m4a
```

Можно указать полный путь:

```bash
python transcribe.py transcribe ~/Downloads/audio.m4a
```

Скрипт сохранит результат рядом с исходным аудиофайлом:

```text
audio.m4a
audio.txt
audio.json
```

`audio.txt` содержит текст расшифровки.

`audio.json` содержит полный ответ API, включая временные метки и информацию о говорящих.

Для русской речи используется `language_code=rus`.

### GET — получение транскрипции

Получить транскрипцию по её ID:

```bash
python transcribe.py get TRANSCRIPTION_ID
```

Например:

```bash
python transcribe.py get abc123
```

Результат будет сохранён в текущей папке:

```text
transcript_abc123.txt
transcript_abc123.json
```

### DELETE — удаление транскрипции

Удалить транскрипцию по ID:

```bash
python transcribe.py delete TRANSCRIPTION_ID
```

Перед удалением скрипт попросит ввести ID для подтверждения.

Удаление происходит на стороне ElevenLabs и не может быть отменено.

## Зависимости

- requests
- python-dotenv

## API

Используется ElevenLabs Speech-to-Text API:

https://elevenlabs.io/docs/api-reference/speech-to-text/convert

https://elevenlabs.io/docs/api-reference/speech-to-text/get

https://elevenlabs.io/docs/api-reference/speech-to-text/delete

