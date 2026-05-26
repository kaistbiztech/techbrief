#!/usr/bin/env python3
"""
Daily Tech Brief - 카톡 공유 산출물 생성기

입력: data/YYYY-MM-DD.json
출력:
  - Message/YYYY-MM-DD/card.png   (로컬 카톡 첨부 사본)
  - Message/YYYY-MM-DD/text.txt   (로컬 카톡 복붙 텍스트)
  - date/YYYY-MM-DD/og.png        (사이트 OG 이미지, 깃 푸시)

OG 메타가 박힌 일자별 정적 HTML은 build_site.py가 생성한다.

사용법:
    python generate_message.py data/2026-05-26.json [--project-root <dailytechbrief-root>]
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

SITE_URL = "https://kaistbiztech.github.io/dailytechbrief/"
PROJECT_ROOT = None
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
KAKAO_TEMPLATE = TEMPLATES_DIR / "kakao-card.html"   # 9:16 세로, 카톡 앱 첨부용
OG_TEMPLATE = TEMPLATES_DIR / "og-card.html"          # 1.91:1 가로, 메신저 OG 미리보기용
MESSAGE_BASE = None
DATE_BASE = None
LOGO_PATH = None


def _is_project_root(path: Path) -> bool:
    return (path / "index.html").is_file() and (path / "data").is_dir()


def _walk_for_project_root(start: Path) -> Path | None:
    start = start.resolve()
    candidates = [start] + list(start.parents)
    for candidate in candidates:
        if _is_project_root(candidate):
            return candidate
    return None


def resolve_project_root(json_arg: Path, explicit: str | None = None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    if os.environ.get("DAILYTECHBRIEF_ROOT"):
        candidates.append(Path(os.environ["DAILYTECHBRIEF_ROOT"]))
    candidates.extend([json_arg, Path.cwd()])

    for candidate in candidates:
        found = _walk_for_project_root(candidate)
        if found:
            return found

    raise SystemExit(
        "Project root not found. Run from the dailytechbrief repo or pass --project-root."
    )


def configure_paths(project_root: Path) -> None:
    global PROJECT_ROOT, MESSAGE_BASE, DATE_BASE, LOGO_PATH
    PROJECT_ROOT = project_root
    MESSAGE_BASE = PROJECT_ROOT / "Message"
    DATE_BASE = PROJECT_ROOT / "date"
    LOGO_PATH = PROJECT_ROOT / "KCB_Logo.png"


def build_text(edition: dict) -> str:
    """카톡 복붙용 텍스트 — 사이트 링크 상단, KAIST 프레임, 키워드, 3문장 요약."""
    date_str = edition["id"].replace("-", ".")
    dow = edition.get("dayOfWeek", "")
    eid = edition["id"]

    parts = []
    parts.append("📰 KAIST 경영대학 테크 네트워크")
    parts.append("데일리 테크 브리프")
    parts.append(f"{date_str} {dow}요일")
    parts.append("")
    parts.append(f"전체 보기 👉 {SITE_URL}date/{eid}/")

    # 키워드 묶음
    all_kw = []
    for it in edition["newsItems"]:
        all_kw.extend(it.get("keywords", []))
    if all_kw:
        parts.append("")
        parts.append("🔑 오늘의 키워드")
        parts.append(" · ".join(all_kw))

    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append("")

    for item in edition["newsItems"]:
        parts.append(f"{item['order']:02d}. {item['title']}")
        parts.append(item["summary"])
        parts.append("")

    parts.append("━━━━━━━━━━━━━━━━━━━")
    parts.append(f"전체 보기 👉 {SITE_URL}date/{eid}/")
    parts.append("© KAIST 경영대학 테크 네트워크")
    return "\n".join(parts)


def _logo_data_url() -> str | None:
    import base64
    if not LOGO_PATH.is_file():
        return None
    return "data:image/png;base64," + base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")


def _capture(browser, template_path: Path, edition: dict, viewport: dict, out_path: Path, logo_url: str | None) -> None:
    ctx = browser.new_context(viewport=viewport, device_scale_factor=2)
    page = ctx.new_page()
    page.goto(template_path.resolve().as_uri(), wait_until="networkidle")
    page.evaluate(
        "([ed, logo]) => window.renderEdition(ed, logo)",
        [edition, logo_url],
    )
    page.wait_for_timeout(700)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_path), full_page=False, type="png")
    ctx.close()


def generate_cards(edition: dict, kakao_out: Path, og_out: Path) -> None:
    """
    카톡 앱 첨부용 9:16 세로 카드 + 메신저 OG 1.91:1 가로 카드를 각각 캡처.

    - kakao_out: 1080×1920 (Message/<id>/card.png)
    - og_out: 1200×630 (date/<id>/og.png)
    """
    from playwright.sync_api import sync_playwright

    logo_url = _logo_data_url()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        _capture(browser, KAKAO_TEMPLATE, edition,
                 {"width": 1080, "height": 1920}, kakao_out, logo_url)
        _capture(browser, OG_TEMPLATE, edition,
                 {"width": 1200, "height": 630}, og_out, logo_url)
        browser.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", help="path to data/YYYY-MM-DD.json")
    parser.add_argument("--project-root", help="dailytechbrief repository root")
    args = parser.parse_args()

    json_path = Path(args.json_path)
    project_root = resolve_project_root(json_path, args.project_root)
    configure_paths(project_root)
    if not json_path.is_absolute():
        candidate = (Path.cwd() / json_path).resolve()
        if not candidate.is_file():
            candidate = (project_root / json_path).resolve()
        json_path = candidate
    else:
        json_path = json_path.resolve()

    if not json_path.is_file():
        print(f"Not found: {json_path}", file=sys.stderr)
        return 1

    edition = json.loads(json_path.read_text(encoding="utf-8"))
    eid = edition["id"]

    message_dir = MESSAGE_BASE / eid
    message_dir.mkdir(parents=True, exist_ok=True)
    date_dir = DATE_BASE / eid
    date_dir.mkdir(parents=True, exist_ok=True)

    # 1) 텍스트 (로컬)
    text_path = message_dir / "text.txt"
    text_path.write_text(build_text(edition), encoding="utf-8")
    print(f"[OK] wrote {text_path.relative_to(PROJECT_ROOT)}")

    # 2) 카드 PNG: 카톡용(9:16) + OG용(1.91:1) 각각 캡처
    card_path = message_dir / "card.png"
    og_path = date_dir / "og.png"
    generate_cards(edition, kakao_out=card_path, og_out=og_path)
    print(f"[OK] wrote {card_path.relative_to(PROJECT_ROOT)}")
    print(f"[OK] wrote {og_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
