
import os
import sys
import json
import argparse
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv


# Загружаем API-ключ из .env
load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")

BASE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
TRANSCRIPTS_URL = f"{BASE_URL}/transcripts"

HEADERS = {
    "xi-api-key": API_KEY or "",
}


def save_transcript(result, output_path):
    """Сохраняет текст и полный JSON ответа API."""

    output_path = Path(output_path)

    # Сохраняем текст
    txt_path = output_path.with_suffix(".txt")
    txt_path.write_text(
        result.get("text", ""),
        encoding="utf-8",
    )

    # Сохраняем полный JSON
    json_path = output_path.with_suffix(".json")
    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Текст сохранён: {txt_path}")
    print(f"Полный JSON сохранён: {json_path}")


def handle_api_error(response):
    """Выводит подробности ошибки API."""

    try:
        error = response.json()
        details = json.dumps(
            error,
            ensure_ascii=False,
            indent=2,
        )
    except ValueError:
        details = response.text

    print(f"Ошибка API: HTTP {response.status_code}")
    print(details)

    raise SystemExit(1)


def transcribe(audio_path):
    """POST: отправляет аудио на транскрибирование."""

    audio_path = Path(audio_path).expanduser()

    if not audio_path.is_file():
        raise SystemExit(f"Файл не найден: {audio_path}")

    data = {
        "model_id": "scribe_v2",
        "language_code": "rus",
    }

    print(f"Отправляю файл: {audio_path.name}")

    try:
        with audio_path.open("rb") as audio:
            response = requests.post(
                BASE_URL,
                headers=HEADERS,
                data=data,
                files={
                    "file": (audio_path.name, audio)
                },
                timeout=600,
            )

    except requests.exceptions.RequestException as error:
        raise SystemExit(f"Ошибка соединения: {error}")

    if not response.ok:
        handle_api_error(response)

    result = response.json()

    save_transcript(result, audio_path)

    print()
    print("Транскрибирование завершено!")
    print(f"Язык: {result.get('language_code', 'не определён')}")
    print(f"Элементов в words: {len(result.get('words', []))}")

    transcription_id = result.get("transcription_id")

    if transcription_id:
        print(f"ID транскрипции: {transcription_id}")
        print(f"Получить результат: python transcribe.py get {transcription_id}")
    else:
        print("ID транскрипции не возвращён в ответе API.")

    print()
    print("Расшифровка:")
    print(result.get("text", ""))


def get_transcript(transcription_id):
    """GET: получает ранее созданную транскрипцию по ID."""

    transcription_id = transcription_id.strip()

    if not transcription_id:
        raise SystemExit("Необходимо указать ID транскрипции.")

    safe_id = quote(transcription_id, safe="")
    url = f"{TRANSCRIPTS_URL}/{safe_id}"

    print(f"Получаю транскрипцию: {transcription_id}")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=60,
        )

    except requests.exceptions.RequestException as error:
        raise SystemExit(f"Ошибка соединения: {error}")

    if not response.ok:
        handle_api_error(response)

    result = response.json()

    # Сохраняем результат в текущей папке
    output_path = Path(f"transcript_{transcription_id}")

    save_transcript(result, output_path)

    print()
    print("Транскрипция получена!")
    print(f"Язык: {result.get('language_code', 'не определён')}")
    print()
    print(result.get("text", ""))


def delete_transcript(transcription_id):
    """DELETE: удаляет транскрипцию по ID."""

    transcription_id = transcription_id.strip()

    if not transcription_id:
        raise SystemExit("Необходимо указать ID транскрипции.")

    print(f"ВНИМАНИЕ: будет удалена транскрипция {transcription_id}.")
    print("Это действие нельзя отменить.")

    confirmation = input(
        f"Для подтверждения введи ID транскрипции: "
    ).strip()

    if confirmation != transcription_id:
        print("Удаление отменено.")
        return

    safe_id = quote(transcription_id, safe="")
    url = f"{TRANSCRIPTS_URL}/{safe_id}"

    try:
        response = requests.delete(
            url,
            headers=HEADERS,
            timeout=60,
        )

    except requests.exceptions.RequestException as error:
        raise SystemExit(f"Ошибка соединения: {error}")

    if not response.ok:
        handle_api_error(response)

    print(f"Транскрипция {transcription_id} успешно удалена.")
    if response.text.strip():
        print(f"Ответ API: {response.text}")


def main():
    if not API_KEY:
        raise SystemExit(
            "Ошибка: не найден ELEVENLABS_API_KEY в файле .env"
        )

    parser = argparse.ArgumentParser(
        description="ElevenLabs Speech-to-Text API"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # POST
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Отправить аудио на транскрибирование",
    )
    transcribe_parser.add_argument(
        "file",
        help="Путь к аудиофайлу",
    )

    # GET
    get_parser = subparsers.add_parser(
        "get",
        help="Получить транскрипцию по ID",
    )
    get_parser.add_argument(
        "transcription_id",
        help="ID транскрипции",
    )

    # DELETE
    delete_parser = subparsers.add_parser(
        "delete",
        help="Удалить транскрипцию по ID",
    )
    delete_parser.add_argument(
        "transcription_id",
        help="ID транскрипции",
    )

    # Поддержка старого способа запуска:
    # python transcribe.py audio.m4a
    args_list = sys.argv[1:]

    if args_list and args_list[0] not in {
        "transcribe",
        "get",
        "delete",
        "-h",
        "--help",
    }:
        args_list.insert(0, "transcribe")

    args = parser.parse_args(args_list)

    if args.command == "transcribe":
        transcribe(args.file)

    elif args.command == "get":
        get_transcript(args.transcription_id)

    elif args.command == "delete":
        delete_transcript(args.transcription_id)


if __name__ == "__main__":
    main()

