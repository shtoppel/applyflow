import re
import logging
from dataclasses import dataclass
from typing import Literal, List

# Настройка вывода в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ParsedGmailEvent:
    event: str
    company_name: str | None = None
    reason: str | None = None


class GmailRuleParser:
    # Самые простые маркеры
    KEYWORDS = {
        "accepted": [r"offer", r"angebot", r"vertrag", r"welcome"],
        "interview": [r"gespr[aä]ch", r"interview", r"termin", r"call", r"einladen"],
        "rejected": [r"absage", r"unfortunately", r"rejection", r"nicht ber[üu]cksichtigen"],
        "in_review": [r"bewerbung", r"application", r"eingangen", r"received", r"dank"]
    }

    def __init__(self, target_companies: List[str]):
        self.target_companies = target_companies

    def parse(self, sender, subject, snippet):
        # Собираем текст
        raw_text = f"{sender} {subject} {snippet}"

        # Очистка (нормализация)
        clean_text = raw_text.replace('\xa0', ' ').lower()
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # ВОТ ЭТО ВЫВЕДЕТСЯ В КОНСОЛЬ PYCHARM:
        logger.info(f"--- ЧТО ВИДИТ ПАРСЕР ---")
        logger.info(f"TEXT: {clean_text}")
        logger.info(f"COMPANIES TO SEARCH: {self.target_companies}")

        # 1. Ищем компанию
        found_company = None
        for company in self.target_companies:
            if company.lower() in clean_text:
                found_company = company
                break

        if not found_company:
            logger.warning("РЕЗУЛЬТАТ: Компания не найдена в тексте!")
            return ParsedGmailEvent("unknown", reason="No company match")

        # 2. Ищем статус
        for event_name, patterns in self.KEYWORDS.items():
            for p in patterns:
                if re.search(p, clean_text, re.IGNORECASE):
                    logger.info(f"РЕЗУЛЬТАТ: Найдено совпадение! Статус: {event_name}, Правило: {p}")
                    return ParsedGmailEvent(event_name, found_company, f"Match: {p}")

        logger.warning(f"РЕЗУЛЬТАТ: Компания '{found_company}' найдена, но ни одно ключевое слово не подошло.")
        return ParsedGmailEvent("unknown", found_company, "Status keywords not found")


# --- ЗАПУСК ДЛЯ ПРОВЕРКИ ---
if __name__ == "__main__":
    # 1. Впиши сюда названия компаний, которые ты ждешь
    my_parser = GmailRuleParser(["q.beyond AG", "Google", "Zalando"])

    # 2. Вставь сюда данные из РЕАЛЬНОГО письма, которое не парсится
    test_res = my_parser.parse(
        sender="karriere@qbeyond.de",
        subject="Eingangsbestätigung",
        snippet="vielen Dank für deine Bewerbung als Initiativbewerbung"
    )

    print("\n--- ИТОГОВЫЙ ОБЪЕКТ ---")
    print(test_res)