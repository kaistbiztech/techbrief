#!/usr/bin/env python3
"""Validate one KAIST Daily Tech Brief JSON file.

This script is intentionally deterministic so automation runs do not need to
rewrite ad hoc validation code.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse


KOREAN_MEDIA_DOMAINS = {
    "zdnet.co.kr",
    "etnews.com",
    "newsis.com",
    "hankyung.com",
    "news1.kr",
    "fnnews.com",
    "dailian.co.kr",
    "newsway.co.kr",
    "chosun.com",
    "joongang.co.kr",
    "mk.co.kr",
    "sedaily.com",
    "yna.co.kr",
}

KOREA_MARKERS = {
    "한국",
    "국내",
    "금융위",
    "과기정통부",
    "KAIST",
    "카이스트",
    "삼성",
    "SK",
    "LG",
    "현대",
    "카카오",
    "네이버",
    "토스",
    "업스테이지",
    "리벨리온",
    "퓨리오사",
    "인천",
    "서울",
    "국방",
    "금융",
    "제조업",
}

NEWSLETTER_OR_INSIGHT_DOMAINS = {
    "every.to",
    "stratechery.com",
    "substack.com",
    "ben-evans.com",
    "theinformation.com",
}

NEWSLETTER_OR_INSIGHT_NAMES = {
    "Every",
    "Stratechery",
    "Benedict Evans",
    "The Information",
    "Context Window",
}

FORBIDDEN_WORDS = {"충격", "역대급", "대박", "미쳤다", "엄청난", "굉장한"}
FORBIDDEN_AI_PHRASES = {"결론적으로", "요컨대", "다음과 같이", "라고 합니다"}
DAY_NAMES = {"월", "화", "수", "목", "금", "토", "일"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_domain_or_subdomain(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def has_any_domain(url: str, domains: set[str]) -> bool:
    host = domain_of(url)
    return any(is_domain_or_subdomain(host, domain) for domain in domains)


def is_korean_source(source: dict) -> bool:
    return has_any_domain(source.get("url", ""), KOREAN_MEDIA_DOMAINS)


def is_newsletter_or_insight_source(source: dict) -> bool:
    name = source.get("name", "")
    url = source.get("url", "")
    return name in NEWSLETTER_OR_INSIGHT_NAMES or has_any_domain(
        url, NEWSLETTER_OR_INSIGHT_DOMAINS
    )


def summary_sentence_count(summary: str) -> int:
    # Count Korean sentence-ending periods. Decimal points such as "0.025" are ignored.
    return len(re.findall(r"(?<=[가-힣])\.(?:\s|$)", summary))


def title_has_number(title: str) -> bool:
    return bool(re.search(r"\d|%|천|만|억|조", title))


def title_has_named_entity(title: str, item: dict) -> bool:
    first_keyword = item.get("keywords", [""])[0] if item.get("keywords") else ""
    if first_keyword and first_keyword in title:
        return True
    return bool(re.search(r"[A-Za-z]{2,}|[가-힣]{2,}", title))


def is_korea_related(item: dict) -> bool:
    text = " ".join(
        [
            item.get("title", ""),
            item.get("summary", ""),
            " ".join(item.get("keywords", [])),
        ]
    )
    return any(marker in text for marker in KOREA_MARKERS) or any(
        is_korean_source(source) for source in item.get("sources", [])
    )


def recent_issue_files(data_dir: Path, issue_id: str, days: int) -> list[Path]:
    issue_date = date.fromisoformat(issue_id)
    start = issue_date - timedelta(days=days)
    files: list[Path] = []
    for path in data_dir.glob("*.json"):
        if ".bak-" in path.name:
            continue
        try:
            file_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if start <= file_date < issue_date:
            files.append(path)
    return sorted(files)


def normalize_topic_terms(item: dict) -> set[str]:
    terms = set()
    for value in item.get("keywords", []):
        if value:
            terms.add(str(value).strip().lower())
    for token in re.findall(r"[A-Za-z0-9가-힣]+", item.get("title", "")):
        if len(token) >= 3:
            terms.add(token.lower())
    return terms


def validate(data: dict, json_path: Path, recent_days: int) -> list[str]:
    errors: list[str] = []
    issue_id = data.get("id", "")
    items = data.get("newsItems", [])

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", issue_id):
        errors.append("id must be YYYY-MM-DD")
        return errors

    if json_path.name != f"{issue_id}.json":
        errors.append("filename must match id")

    if data.get("dayOfWeek") not in DAY_NAMES:
        errors.append("dayOfWeek must be one of 월,화,수,목,금,토,일")

    coverage = data.get("coverage") or {}
    try:
        coverage_from = date.fromisoformat(coverage.get("from", ""))
        coverage_to = date.fromisoformat(coverage.get("to", ""))
    except ValueError:
        errors.append("coverage.from/to must be valid YYYY-MM-DD dates")
        return errors

    if len(items) != 10:
        errors.append(f"newsItems length must be 10, got {len(items)}")

    orders = [item.get("order") for item in items]
    if orders != list(range(1, 11)):
        errors.append(f"order values must be exactly 1..10 in order, got {orders}")

    korea_related_count = 0
    newsletter_or_insight_count = 0

    for item in items:
        order = item.get("order", "?")
        title = item.get("title", "")
        summary = item.get("summary", "")
        sources = item.get("sources", [])

        for field in ["order", "title", "summary", "eventDate", "keywords", "sources"]:
            if field not in item:
                errors.append(f"item {order}: missing {field}")

        try:
            event_date = date.fromisoformat(item.get("eventDate", ""))
            if not (coverage_from <= event_date <= coverage_to):
                errors.append(
                    f"item {order}: eventDate {event_date.isoformat()} outside coverage"
                )
        except ValueError:
            errors.append(f"item {order}: invalid eventDate")

        if not title_has_number(title):
            errors.append(f"item {order}: title lacks a key number")

        if not title_has_named_entity(title, item):
            errors.append(f"item {order}: title lacks a named entity")

        if summary_sentence_count(summary) != 3:
            errors.append(
                f"item {order}: summary must have exactly 3 Korean sentences"
            )

        if any(mark in summary for mark in ["\n", "•"]) or re.search(
            r"(^|\s)([-*]|\d+[.)])\s", summary
        ):
            errors.append(f"item {order}: summary contains list-like formatting")

        if any(word in summary or word in title for word in FORBIDDEN_WORDS):
            errors.append(f"item {order}: contains forbidden hype word")

        if any(phrase in summary for phrase in FORBIDDEN_AI_PHRASES):
            errors.append(f"item {order}: contains forbidden AI stock phrase")

        if "$" in summary or "달러" in summary:
            if "원" not in summary:
                errors.append(f"item {order}: dollar amount lacks local currency context")

        if not isinstance(sources, list) or not sources:
            errors.append(f"item {order}: sources must be a non-empty array")
            continue

        korean_positions = []
        for index, source in enumerate(sources):
            name = source.get("name")
            url = source.get("url")
            if not name or not url:
                errors.append(f"item {order}: source missing name or url")
            elif not url.startswith("https://"):
                errors.append(f"item {order}: source URL must start with https://")
            if is_korean_source(source):
                korean_positions.append(index)
            if is_newsletter_or_insight_source(source):
                newsletter_or_insight_count += 1

        if korean_positions and korean_positions[0] != 0:
            errors.append(f"item {order}: Korean media source must be first")

        if is_korea_related(item):
            korea_related_count += 1

    if korea_related_count < 4:
        errors.append(f"Korea-related item count must be >= 4, got {korea_related_count}")

    if newsletter_or_insight_count < 1:
        errors.append("at least one newsletter/blog/insight item is required")

    recent_files = recent_issue_files(json_path.parent, issue_id, recent_days)
    current_topics = [(item.get("order"), normalize_topic_terms(item)) for item in items]
    for recent_file in recent_files:
        recent = load_json(recent_file)
        for old_item in recent.get("newsItems", []):
            old_terms = normalize_topic_terms(old_item)
            for order, terms in current_topics:
                overlap = terms & old_terms
                if len(overlap) >= 3:
                    errors.append(
                        f"item {order}: possible duplicate with {recent_file.name} "
                        f"item {old_item.get('order')} ({', '.join(sorted(overlap)[:5])})"
                    )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=Path)
    parser.add_argument("--recent-days", type=int, default=7)
    args = parser.parse_args()

    try:
        data = load_json(args.json_path)
    except Exception as exc:  # noqa: BLE001 - print concise CLI failure
        print(f"SELF_CHECK=FAIL\n- JSON parsing failed: {exc}")
        return 1

    errors = validate(data, args.json_path, args.recent_days)
    if errors:
        print("SELF_CHECK=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    korea_count = sum(is_korea_related(item) for item in data["newsItems"])
    insight_count = sum(
        any(is_newsletter_or_insight_source(source) for source in item["sources"])
        for item in data["newsItems"]
    )
    coverage = data["coverage"]
    print("SELF_CHECK=PASS")
    print(f"id={data['id']}")
    print(f"coverage={coverage['from']}..{coverage['to']}")
    print("items=10 orders=1..10")
    print(f"korea_related={korea_count}")
    print(f"newsletter_blog_insight={insight_count}")
    print(f"recent_duplicate_check_days={args.recent_days}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
