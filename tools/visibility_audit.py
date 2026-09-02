#!/usr/bin/env python3
"""Measure technical visibility readiness without inventing search outcomes.

Local mode validates repository state. Live mode additionally checks the public
origin after deployment. The output explicitly leaves ranking, indexing,
referral, and external-citation fields unmeasured until an authoritative data
source is connected.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_HTML = {"404.html", "google904951439b331720.html"}
CANONICAL_RE = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
SCRIPT_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)
AUTHOR_ID = "https://ahmed-alhafiz.github.io/#person"
USER_AGENT = "AhmedAlhafiz-Visibility-Audit/1.0 (+https://ahmed-alhafiz.github.io/about/)"


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "svg"}:
            self.suppressed += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "svg"} and self.suppressed:
            self.suppressed -= 1

    def handle_data(self, data: str) -> None:
        if not self.suppressed:
            self.parts.append(data)

    @property
    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def public_html() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and path.name not in EXCLUDED_HTML
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_robots(text: str) -> dict[str, list[str]]:
    policies: dict[str, list[str]] = {}
    current: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        if key.lower() == "user-agent":
            current = [value]
            policies.setdefault(value, [])
        elif key.lower() in {"allow", "disallow"}:
            for agent in current:
                policies.setdefault(agent, []).append(f"{key.title()}: {value}")
    return policies


def iter_nodes(value: object):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from iter_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_nodes(child)


def local_audit() -> dict[str, Any]:
    errors: list[str] = []
    baseline = load_json(ROOT / "data/visibility-baseline.json")
    inventory = load_json(ROOT / "data/content-inventory.json")
    manifest = load_json(ROOT / "author.json")

    pages = public_html()
    canonicals: list[str] = []
    author_links = 0
    manifest_links = 0
    person_nodes = 0
    for path in pages:
        html = path.read_text(encoding="utf-8")
        matches = CANONICAL_RE.findall(html)
        if len(matches) != 1:
            errors.append(f"{path.relative_to(ROOT)}: expected one canonical, found {len(matches)}")
        else:
            canonicals.append(matches[0])
        author_links += html.count('rel="author"')
        manifest_links += html.count('type="application/ld+json" href="/author.json"')
        for block in SCRIPT_RE.findall(html):
            data = json.loads(block)
            for node in iter_nodes(data):
                if isinstance(node, dict) and node.get("@type") == "Person" and node.get("@id") == AUTHOR_ID:
                    person_nodes += 1

    if len(set(canonicals)) != len(canonicals):
        errors.append("Duplicate canonical URLs found")

    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_tree = ET.parse(ROOT / "sitemap.xml")
    sitemap_urls = [node.text or "" for node in sitemap_tree.findall(".//s:loc", namespace)]
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append("Duplicate sitemap URLs found")
    canonical_set = set(canonicals)
    sitemap_set = set(sitemap_urls)
    if canonical_set != sitemap_set:
        errors.append(
            "Canonical/sitemap mismatch: "
            f"missing_from_sitemap={sorted(canonical_set - sitemap_set)}, "
            f"missing_pages={sorted(sitemap_set - canonical_set)}"
        )

    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    policies = parse_robots(robots_text)
    for agent in ("OAI-SearchBot", "GPTBot", "*"):
        if "Allow: /" not in policies.get(agent, []):
            errors.append(f"robots.txt: {agent} is not explicitly allowed at root")

    graph = manifest.get("@graph", [])
    persons = [
        node
        for node in graph
        if isinstance(node, dict)
        and node.get("@type") == "Person"
        and node.get("@id") == AUTHOR_ID
    ]
    if len(persons) != 1:
        errors.append(f"author.json: expected one canonical Person, found {len(persons)}")

    ar_feed = load_json(ROOT / "articles/feed.json")
    en_feed = load_json(ROOT / "en/articles/feed.json")
    research_index = load_json(ROOT / "articles/research-index.json")
    class_counts: dict[str, int] = {}
    for item in inventory.get("items", []):
        item_class = item.get("class", "missing")
        class_counts[item_class] = class_counts.get(item_class, 0) + 1
    if class_counts != inventory.get("current_counts"):
        errors.append("data/content-inventory.json: declared counts do not match items")

    measured = {
        "public_html_pages": len(pages),
        "canonical_urls": len(canonicals),
        "sitemap_urls": len(sitemap_urls),
        "research_items": len(research_index.get("items", [])),
        "arabic_feed_items": len(ar_feed.get("items", [])),
        "english_feed_items": len(en_feed.get("items", [])),
        "author_rel_links": author_links,
        "author_manifest_links": manifest_links,
        "canonical_person_nodes": person_nodes,
        "content_classes": class_counts,
        "crawler_policies": policies,
    }

    expected = baseline.get("technical_baseline", {})
    checks = {
        "public_html_pages": len(pages),
        "canonical_urls": len(canonicals),
        "sitemap_urls": len(sitemap_urls),
        "research_items": len(research_index.get("items", [])),
        "arabic_feed_items": len(ar_feed.get("items", [])),
        "english_feed_items": len(en_feed.get("items", [])),
    }
    for key, actual in checks.items():
        declared = expected.get(key)
        if declared != actual:
            errors.append(f"visibility baseline drift: {key} declares {declared}, measured {actual}")

    if author_links != len(pages):
        errors.append(f"Expected one rel=author per public page: {author_links}/{len(pages)}")
    if manifest_links != len(pages):
        errors.append(f"Expected one author.json link per public page: {manifest_links}/{len(pages)}")

    return {
        "status": "failed" if errors else "passed",
        "errors": errors,
        "measured": measured,
        "unmeasured_external_outcomes": baseline.get("observed_outcomes", {}),
    }


def fetch_url(url: str, *, attempts: int = 4, delay: float = 3.0) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, attempts + 1):
        separator = "&" if "?" in url else "?"
        cache_busted = f"{url}{separator}visibility_audit={int(time.time())}-{attempt}"
        request = urllib.request.Request(
            cache_busted,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/json,application/xml,text/plain;q=0.9,*/*;q=0.5",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                body = response.read(3_000_000)
                return {
                    "url": url,
                    "status": response.status,
                    "content_type": response.headers.get_content_type(),
                    "content_length": len(body),
                    "etag": response.headers.get("ETag"),
                    "last_modified": response.headers.get("Last-Modified"),
                    "body": body.decode("utf-8", errors="replace"),
                }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < attempts:
                time.sleep(delay * attempt)
    return {"url": url, "status": None, "error": last_error, "body": ""}


def live_audit(origin: str) -> dict[str, Any]:
    errors: list[str] = []
    origin = origin.rstrip("/")
    inventory = load_json(ROOT / "data/content-inventory.json")
    critical_routes = [
        "/",
        "/about/",
        "/en/about/",
        "/de/about/",
        "/author.json",
        "/robots.txt",
        "/sitemap.xml",
        "/articles/feed.json",
        "/en/articles/feed.json",
        "/articles/research-index.json",
    ]
    critical_routes.extend(
        urllib.parse.urlparse(item["url"]).path
        for item in inventory.get("items", [])
        if item.get("class") in {"pillar", "pillar_candidate"}
    )
    critical_routes = list(dict.fromkeys(critical_routes))

    # The manifest is new in this release. Poll it long enough for Pages to finish.
    manifest_url = origin + "/author.json"
    manifest_result = fetch_url(manifest_url, attempts=18, delay=5.0)
    results: dict[str, dict[str, Any]] = {"/author.json": manifest_result}
    if manifest_result.get("status") != 200 or AUTHOR_ID not in manifest_result.get("body", ""):
        errors.append(f"live author manifest not deployed correctly: {manifest_result.get('error') or manifest_result.get('status')}")

    for route in critical_routes:
        if route == "/author.json":
            continue
        result = fetch_url(origin + route, attempts=4, delay=2.0)
        results[route] = result
        if result.get("status") != 200:
            errors.append(f"live {route}: expected HTTP 200, found {result.get('status')} ({result.get('error', '')})")
            continue
        body = result.get("body", "")
        if route in {"/about/", "/en/about/", "/de/about/"}:
            if 'id="identity"' not in body or "/author.json" not in body:
                errors.append(f"live {route}: visible identity section or manifest link missing")
        if route == "/robots.txt":
            policies = parse_robots(body)
            for agent in ("OAI-SearchBot", "GPTBot", "*"):
                if "Allow: /" not in policies.get(agent, []):
                    errors.append(f"live robots.txt: {agent} is not explicitly allowed")
        if route.endswith("feed.json"):
            try:
                json.loads(body)
            except json.JSONDecodeError as exc:
                errors.append(f"live {route}: invalid JSON feed: {exc}")
        if route == "/articles/research-index.json":
            try:
                index = json.loads(body)
                if len(index.get("items", [])) != 9:
                    errors.append(f"live research index: expected 9 items, found {len(index.get('items', []))}")
            except json.JSONDecodeError as exc:
                errors.append(f"live research index invalid JSON: {exc}")
        if route == "/sitemap.xml":
            try:
                ET.fromstring(body)
            except ET.ParseError as exc:
                errors.append(f"live sitemap invalid XML: {exc}")

    public_results = {
        route: {key: value for key, value in result.items() if key != "body"}
        for route, result in results.items()
    }
    return {
        "status": "failed" if errors else "passed",
        "origin": origin,
        "errors": errors,
        "requests": public_results,
        "interpretation": "HTTP and content checks prove deployment accessibility only; they do not prove indexing, ranking, or citation.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="also audit the deployed public origin")
    parser.add_argument("--origin", default=None, help="override canonical origin for live checks")
    parser.add_argument("--output", default=None, help="write the JSON report to this path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    baseline = load_json(ROOT / "data/visibility-baseline.json")
    origin = args.origin or baseline["site"]["canonical_origin"]
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "origin": origin,
        "local": local_audit(),
        "external_outcome_boundary": {
            "google_rankings": "not measured by this tool",
            "indexed_page_count": "not measured by this tool",
            "knowledge_panel": "not measured by this tool",
            "ai_citations": "not measured by this tool",
            "referral_sessions": "not measured by this tool",
        },
    }
    if args.live:
        report["live"] = live_audit(origin)
    status = report["local"]["status"] == "passed" and (
        not args.live or report.get("live", {}).get("status") == "passed"
    )
    report["status"] = "passed" if status else "failed"

    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(serialized, encoding="utf-8")
    print(serialized)
    if not status:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
