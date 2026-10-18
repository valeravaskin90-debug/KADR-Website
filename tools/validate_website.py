"""Validate the buildless KADR website without network access."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "website"
PAGES = (SITE / "index.html", SITE / "docs.html", SITE / "en" / "index.html", SITE / "en" / "docs.html")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.images: list[tuple[str, str | None]] = []
        self.lang: str | None = None
        self.title_depth = 0
        self.title = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "a" and values.get("href"):
            self.links.append(str(values["href"]))
        if tag == "img" and values.get("src"):
            self.images.append((str(values["src"]), values.get("alt")))
        if tag == "title":
            self.title_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.title_depth = max(0, self.title_depth - 1)

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title += data


def resolve_local(page: Path, raw: str) -> tuple[Path, str]:
    parsed = urlsplit(raw)
    target = unquote(parsed.path)
    resolved = page if not target else (page.parent / target).resolve()
    return resolved, parsed.fragment


def main() -> int:
    errors: list[str] = []
    parsed_pages: dict[Path, PageParser] = {}
    for page in PAGES:
        if not page.is_file():
            errors.append(f"missing page: {page.relative_to(ROOT)}")
            continue
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed_pages[page.resolve()] = parser
        expected_lang = "en" if page.parent.name == "en" else "ru"
        if parser.lang != expected_lang:
            errors.append(f"{page.name}: lang={parser.lang!r}, expected {expected_lang!r}")
        if not parser.title.strip():
            errors.append(f"{page.name}: empty title")
        for src, alt in parser.images:
            asset, _ = resolve_local(page, src)
            if not asset.is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing image {src}")
            if alt is None:
                errors.append(f"{page.relative_to(ROOT)}: image has no alt attribute: {src}")

    for page, parser in parsed_pages.items():
        for href in parser.links:
            parsed = urlsplit(href)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            if parsed.scheme or href.startswith("//"):
                errors.append(f"{page.relative_to(ROOT)}: unsupported link {href}")
                continue
            target, fragment = resolve_local(page, href)
            if not target.is_file():
                errors.append(f"{page.relative_to(ROOT)}: missing link target {href}")
                continue
            if fragment and target.suffix.lower() in {".html", ".htm"}:
                target_parser = parsed_pages.get(target)
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    parsed_pages[target] = target_parser
                if fragment not in target_parser.ids:
                    errors.append(f"{page.relative_to(ROOT)}: missing fragment #{fragment} in {target.relative_to(ROOT)}")

    css = SITE / "styles.css"
    script = SITE / "app.js"
    for required in (css, script, SITE / "assets" / "kompas-assembly-real.png", SITE / "assets" / "kadr-ocr-real.png"):
        if not required.is_file() or required.stat().st_size == 0:
            errors.append(f"missing or empty required asset: {required.relative_to(ROOT)}")

    if errors:
        print("WEBSITE VALIDATION: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"WEBSITE VALIDATION: PASS ({len(PAGES)} pages, local links and assets resolved)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

