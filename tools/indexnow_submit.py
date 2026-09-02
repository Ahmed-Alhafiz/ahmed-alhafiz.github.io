#!/usr/bin/env python3
"""Build and optionally submit a standards-compliant IndexNow URL batch.

The client submits only public URLs that changed between two Git commits, or
all sitemap URLs when explicitly requested. It validates host ownership, caps
the batch, records the transport response, and never labels receipt as crawl,
indexing, ranking, or citation.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/indexnow-config.json"
CANONICAL_RE = re.compile(
    r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
USER_AGENT = "AhmedAlhafiz-IndexNow/1.0 (+https://ahmed-alhafiz.github.io/about/)"
PUBLIC_MACHINE_PATHS = {
    "author.json",
    "robots.txt",
    "sitemap.xml",
    "articles/feed.xml",
    "articles/feed.json",
    "articles/research-index.json",
    "en/articles/feed.xml",
    "en/articles/feed.json",
}


def load_config() -> dict[str, Any]:
    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    required = (
        "endpoint",
        "canonical_origin",
        "host",
        "key",
        "key_file",
        "key_location",
        "maximum_urls_per_request",
        "accepted_transport_codes",
    )
    missing = [key for key in required if key not in data]
    if missing:
        raise SystemExit(f"IndexNow configuration missing: {missing}")
    if not data.get("enabled"):
        raise SystemExit("IndexNow configuration is disabled")
    key = str(data["key"])
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise SystemExit("IndexNow key does not meet protocol length/character rules")
    key_path = ROOT / str(data["key_file"])
    if not key_path.is_file() or key_path.read_text(encoding="utf-8").strip() != key:
        raise SystemExit("IndexNow root key file is missing or does not match configuration")
    parsed_origin = urllib.parse.urlparse(str(data["canonical_origin"]))
    parsed_key = urllib.parse.urlparse(str(data["key_location"]))
    if parsed_origin.scheme != "https" or parsed_origin.hostname != data["host"]:
        raise SystemExit("IndexNow canonical origin/host mismatch")
    if parsed_key.hostname != data["host"] or parsed_key.path != "/" + data["key_file"]:
        raise SystemExit("IndexNow key location must be the configured root key file")
    return data


def run_git(*args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {process.stderr.strip()}")
    return process.stdout


def sitemap_urls(origin: str) -> list[str]:
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(ROOT / "sitemap.xml")
    urls = [node.text or "" for node in tree.findall(".//s:loc", namespace)]
    return sorted(url for url in urls if url.startswith(origin.rstrip("/") + "/"))


def path_to_url(path: str, origin: str) -> str | None:
    clean = path.strip().lstrip("./")
    if clean.endswith(".html"):
        file_path = ROOT / clean
        if file_path.is_file():
            html = file_path.read_text(encoding="utf-8")
            matches = CANONICAL_RE.findall(html)
            if len(matches) == 1:
                return matches[0]
        if clean == "index.html":
            return origin.rstrip("/") + "/"
        if clean.endswith("/index.html"):
            return origin.rstrip("/") + "/" + clean[: -len("index.html")]
        return origin.rstrip("/") + "/" + clean
    if clean in PUBLIC_MACHINE_PATHS:
        return origin.rstrip("/") + "/" + clean
    return None


def changed_paths(before: str, after: str) -> list[tuple[str, str]]:
    if not before or set(before) == {"0"}:
        return []
    output = run_git("diff", "--name-status", before, after, "--")
    results: list[tuple[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            results.append(("D", parts[1]))
            results.append(("A", parts[2]))
        elif len(parts) >= 2:
            results.append((status[0], parts[1]))
    return results


def build_urls(config: dict[str, Any], *, before: str | None, after: str | None, submit_all: bool) -> tuple[list[str], list[dict[str, str]]]:
    origin = str(config["canonical_origin"]).rstrip("/")
    changes: list[dict[str, str]] = []
    if submit_all:
        urls = sitemap_urls(origin)
        urls.extend(origin + "/" + path for path in sorted(PUBLIC_MACHINE_PATHS))
        return sorted(set(urls)), [{"status": "ALL", "path": "sitemap_and_machine_surfaces"}]

    if not before or not after:
        raise SystemExit("Changed-URL mode requires --before and --after")
    pairs = changed_paths(before, after)
    if not pairs:
        # A zero/unknown predecessor is safer as an explicit full submission.
        urls = sitemap_urls(origin)
        urls.extend(origin + "/" + path for path in sorted(PUBLIC_MACHINE_PATHS))
        return sorted(set(urls)), [{"status": "FALLBACK_ALL", "path": "no_resolvable_diff"}]

    urls: set[str] = set()
    for status, path in pairs:
        url = path_to_url(path, origin)
        if url:
            urls.add(url)
            changes.append({"status": status, "path": path, "url": url})
    return sorted(urls), changes


def validate_urls(urls: list[str], config: dict[str, Any]) -> None:
    host = config["host"]
    maximum = int(config["maximum_urls_per_request"])
    if len(urls) > maximum:
        raise SystemExit(f"URL batch exceeds configured IndexNow maximum: {len(urls)} > {maximum}")
    for url in urls:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.hostname != host:
            raise SystemExit(f"URL does not belong to configured HTTPS host: {url}")
        if parsed.fragment:
            raise SystemExit(f"Fragments are not submitted to IndexNow: {url}")


def fetch_text(url: str, *, timeout: int = 25) -> tuple[int, str]:
    separator = "&" if "?" in url else "?"
    cache_busted = f"{url}{separator}indexnow_verify={int(time.time())}"
    request = urllib.request.Request(cache_busted, headers={"User-Agent": USER_AGENT, "Accept": "text/plain,*/*;q=0.8"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read(200_000).decode("utf-8", errors="replace")


def wait_for_key(config: dict[str, Any], attempts: int = 24, delay: int = 10) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            status, body = fetch_text(str(config["key_location"]))
            if status == 200 and body.strip() == config["key"]:
                return {"status": "verified", "attempt": attempt, "http_status": status}
            last_error = f"HTTP {status}; body did not match key"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < attempts:
            time.sleep(delay)
    raise SystemExit(f"IndexNow key was not verifiable on the live host: {last_error}")


def submit_batch(urls: list[str], config: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "host": config["host"],
        "key": config["key"],
        "keyLocation": config["key_location"],
        "urlList": urls,
    }
    request = urllib.request.Request(
        str(config["endpoint"]),
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json,text/plain,*/*;q=0.5",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            body = response.read(500_000).decode("utf-8", errors="replace")
            code = response.status
            headers = dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read(500_000).decode("utf-8", errors="replace")
        code = exc.code
        headers = dict(exc.headers.items()) if exc.headers else {}
    accepted = set(int(value) for value in config["accepted_transport_codes"])
    if code not in accepted:
        raise SystemExit(f"IndexNow rejected the batch with HTTP {code}: {body[:1000]}")
    return {
        "transport_status": "received" if code == 200 else "accepted_key_validation_pending",
        "http_status": code,
        "response_body": body,
        "response_headers": {
            key: value
            for key, value in headers.items()
            if key.lower() in {"date", "content-type", "content-length", "server", "request-id", "x-request-id"}
        },
        "interpretation": "Transport success only; crawl, indexing, ranking, and citation remain unproven.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", default=None)
    parser.add_argument("--after", default=None)
    parser.add_argument("--all", action="store_true", dest="submit_all")
    parser.add_argument("--wait-live", action="store_true")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--report", default="indexnow-report.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    urls, changes = build_urls(
        config,
        before=args.before,
        after=args.after,
        submit_all=args.submit_all,
    )
    validate_urls(urls, config)
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "endpoint": config["endpoint"],
        "host": config["host"],
        "key_location": config["key_location"],
        "url_count": len(urls),
        "urls": urls,
        "changes": changes,
        "submission_requested": args.submit,
        "outcome_boundary": "IndexNow transport is not evidence of crawl, indexing, ranking, traffic, or AI citation.",
    }
    if args.wait_live:
        report["key_verification"] = wait_for_key(config)
    if args.submit and urls:
        report["submission"] = submit_batch(urls, config)
        report["status"] = "submitted"
    elif args.submit:
        report["status"] = "no_public_urls_changed"
    else:
        report["status"] = "dry_run"
    Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
