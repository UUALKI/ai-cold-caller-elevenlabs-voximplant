#!/usr/bin/env python3
"""
Простой парсер PDF для пополнения базы знаний `knowledge/company_kb.json`.

- Извлекает текст из переданных PDF
- Ищет кейсы по шаблонам: маршрут, вес, срок
- Ищет факты о компании (название, услуги, метрики) по ключевым словам
- Обновляет JSON, не удаляя существующие записи

Запуск:
  python scripts/pdf_ingest.py "кейсы (2)_compressed (1).pdf" "дорожная карта клиента (1).pdf"
"""

import json
import os
import re
import sys
from typing import List, Dict, Any

# Настройка stdout для Windows-консолей (избежать UnicodeEncodeError)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')  # type: ignore[attr-defined]
except Exception:
    pass

try:
    from pypdf import PdfReader
except Exception:
    # Фолбэк имя пакета
    from PyPDF2 import PdfReader  # type: ignore

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
KB_PATH = os.path.join(ROOT_DIR, 'knowledge', 'company_kb.json')


def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or '')
        except Exception:
            continue
    return "\n".join(texts)


def extract_cases(text: str) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    # Примитивные шаблоны на основе имеющихся примеров
    # Пример: "Шахтная машина" ... "Шанхай" ... "Норильск" ... "Вес груза 35 тонн" ... "Срок доставки 27 дней"
    block_re = re.compile(r"(?P<title>[А-ЯA-Z][^\n]{3,80}?)\s+([\s\S]{0,200}?)\b(Вес\s+груза|Вес|масса)\b\s*(?P<weight>[0-9]+(?:[\.,][0-9]+)?)\s*т(?:онн|)\w*\b[\s\S]{0,100}?\b(Срок\s+доставки|Срок)\b\s*(?P<days>[0-9]+)\s*дн", re.IGNORECASE)
    route_re = re.compile(r"([А-ЯA-Z][а-яa-z\- ]{2,})\s*[—-]\s*([А-ЯA-Z][а-яa-z\- ]{2,})")

    for m in block_re.finditer(text):
        title = m.group('title').strip()
        days = int(float(m.group('days').replace(',', '.')))
        weight = float(m.group('weight').replace(',', '.'))

        # Поиск маршрута рядом
        nearby = text[max(0, m.start()-300): m.end()+300]
        route_match = route_re.search(nearby)
        route = None
        if route_match:
            route = f"{route_match.group(1).strip()} — {route_match.group(2).strip()}"

        cases.append({
            "title": title,
            "route": route,
            "weight_t": weight,
            "days": days
        })

    return cases


def extract_services(text: str) -> List[str]:
    services_keys = [
        "Негабарит", "Авиа", "Морск", "ЖД", "Китай", "Авто"
    ]
    found: List[str] = []
    for key in services_keys:
        if re.search(key, text, re.IGNORECASE):
            found.append(key)
    return list(dict.fromkeys(found))


def load_kb() -> Dict[str, Any]:
    if os.path.exists(KB_PATH):
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"company": {}, "services": [], "cases_short": []}


def save_kb(kb: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(KB_PATH), exist_ok=True)
    with open(KB_PATH, 'w', encoding='utf-8') as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)


def merge_cases(kb: Dict[str, Any], new_cases: List[Dict[str, Any]]) -> None:
    existing = kb.get('cases_short', [])
    seen = {(c.get('title'), c.get('route'), c.get('days')) for c in existing}
    for c in new_cases:
        key = (c.get('title'), c.get('route'), c.get('days'))
        if key not in seen:
            existing.append(c)
            seen.add(key)
    kb['cases_short'] = existing


def merge_services(kb: Dict[str, Any], found_keys: List[str]) -> None:
    # Ничего не удаляем, только отмечаем
    # Можно расширить сопоставлением ключ -> человекочитаемое имя
    return


def main(paths: List[str]) -> None:
    if not paths:
        print("Укажите PDF файлы для парсинга")
        sys.exit(1)

    kb = load_kb()
    total_cases = []

    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(ROOT_DIR, p)
        if not os.path.exists(full):
            print(f"⚠️ Файл не найден: {full}")
            continue
        try:
            txt = read_pdf_text(full)
        except Exception as e:
            print(f"⚠️ Не удалось прочитать {full}: {e}")
            continue

        cases = extract_cases(txt)
        if cases:
            print(f"Найдено кейсов в {os.path.basename(full)}: {len(cases)}")
            total_cases.extend(cases)

        found_services = extract_services(txt)
        if found_services:
            print(f"Найдены упоминания услуг: {', '.join(found_services)}")
            merge_services(kb, found_services)

    if total_cases:
        merge_cases(kb, total_cases)

    save_kb(kb)
    print(f"База знаний обновлена: {KB_PATH}")
    print(f"Кейсов в базе всего: {len(kb.get('cases_short', []))}")


if __name__ == '__main__':
    main(sys.argv[1:])


