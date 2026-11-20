
import os
import sys
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


# Загружаем API-ключ из .env
load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not API_KEY:
    raise SystemExit("Ошибка: не найден ELEVENLABS_API_KEY в .env")


# Получаем путь к аудиофайлу из аргументов командной строки
if len(sys.argv) < 2:
    raise SystemExit(
        "Использование: python transcribe.py путь_к_аудио.mp3"
    )

audio_path = Path(sys.argv[1]).expanduser()

if not audio_path.is_file():
    raise SystemExit(f"Ошибка: файл не найден: {audio_path}")


# Настройки запроса
url = "https://api.elevenlabs.io/v1/speech-to-text"

headers = {
    "xi-api-key": API_KEY,
}

data = {
    "model_id": "scribe_v2",
    "language_code": "rus",
}


# Отправляем аудиофайл в ElevenLabs
print(f"Отправляю файл: {audio_path.name}")

try:
    with audio_path.open("rb") as audio:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files={
                "file": (audio_path.name, audio)
            },
            timeout=600,
        )

    response.raise_for_status()

except requests.exceptions.HTTPError as e:
    print(f"Ошибка API: {e}")
    print(response.text)
    raise SystemExit(1)

except requests.exceptions.RequestException as e:
    raise SystemExit(f"Ошибка соединения: {e}")


# Получаем результат
result = response.json()

text = result.get("text", "")


# Сохраняем обычный текст расшифровки
txt_path = audio_path.with_suffix(".txt")

txt_path.write_text(
    text,
    encoding="utf-8",
)


# Сохраняем полный ответ API в JSON
json_path = audio_path.with_suffix(".json")

json_path.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8",
)


# Выводим информацию в терминал
print()
print("Транскрибирование завершено!")
print(f"Язык: {result.get('language_code', 'не определён')}")
print(f"Уверенность определения языка: {result.get('language_probability', 'не указана')}")
print(f"Количество элементов в words: {len(result.get('words', []))}")
print()
print(f"Текст сохранён: {txt_path}")
print(f"Полный JSON сохранён: {json_path}")
print()
print("Расшифровка:")
print(text)
