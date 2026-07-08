#!/usr/bin/env python3
"""Download and preprocess WA2 Special CHS script files.

This builds a local corpus from the public repository and emits:
- raw/*.txt: downloaded script files
- all_translated_dialogue.tsv: every translated quoted line
- setsuna_candidate_dialogue.tsv: a Snow菜-focused candidate subset
- setsuna_candidate_dialogue.txt: plain text lines for quick distillation

The candidate subset is intentionally conservative about provenance:
it filters by Snow菜-centric story IDs, but does not claim perfect speaker
attribution because the source files do not consistently label speakers.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path


REPO_API = "https://api.github.com/repos/xhyf2666/WhiteAlbum2SpecialCHS/contents/scripts"
RAW_PREFIX = "https://raw.githubusercontent.com/xhyf2666/WhiteAlbum2SpecialCHS/main/scripts/"

# Snow菜-leaning material. This is a heuristic file allowlist, not perfect attribution.
SETSUNA_FILE_PREFIXES = {
    "5100",
    "5101",
    "5102",
    "5103",
    "5104",
    "5300",
    "5301",
    "5302",
    "5303",
    "6001",
    "6002",
    "6003",
    "6004",
    "6005",
    "6101",
    "6102",
    "6103",
    "6104",
    "7000",
    "7200",
    "7300",
}

TRANSLATION_PREFIX = "译文："
QUOTE_RE = re.compile(r"^「(.+?)」$")
TAG_RE = re.compile(r"<[^>]+>")


def fetch_json(url: str) -> object:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "codex-wa2-corpus-builder",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "codex-wa2-corpus-builder"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()

    for encoding in ("utf-8", "utf-8-sig", "cp932", "shift_jis", "gb18030", "big5"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return data.decode("utf-8", errors="replace")


def normalize_line(text: str) -> str:
    text = text.strip()
    text = TAG_RE.sub("", text)
    return text.strip()


def extract_dialogue_rows(file_name: str, text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    source_id = file_name.split("_", 1)[0]
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = normalize_line(raw_line)
        if not line.startswith(TRANSLATION_PREFIX):
            continue

        content = normalize_line(line[len(TRANSLATION_PREFIX) :])
        if not content:
            continue

        match = QUOTE_RE.match(content)
        if not match:
            continue

        rows.append(
            {
                "file": file_name,
                "source_id": source_id,
                "line_no": str(line_no),
                "translation": match.group(1),
                "raw_translation": content,
            }
        )
    return rows


def is_setsuna_candidate(row: dict[str, str]) -> bool:
    if row["source_id"] not in SETSUNA_FILE_PREFIXES:
        return False

    line = row["translation"]
    if len(line) < 2:
        return False

    # Filter out obvious system noise and scene punctuation.
    if all(ch in "…—！？!?" for ch in line):
        return False

    return True


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def build_corpus(output_dir: Path) -> None:
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        listing = fetch_json(REPO_API)
    except urllib.error.URLError as exc:
        raise SystemExit(f"failed to fetch repository listing: {exc}") from exc

    if not isinstance(listing, list):
        raise SystemExit("unexpected repository listing format")

    all_rows: list[dict[str, str]] = []

    for item in listing:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        download_url = item.get("download_url")
        if not isinstance(name, str) or not name.endswith(".txt"):
            continue
        if not isinstance(download_url, str):
            download_url = RAW_PREFIX + name

        text = fetch_text(download_url)
        (raw_dir / name).write_text(text, encoding="utf-8")
        all_rows.extend(extract_dialogue_rows(name, text))

    all_rows.sort(key=lambda row: (row["file"], int(row["line_no"])))
    candidate_rows = [row for row in all_rows if is_setsuna_candidate(row)]

    quotes_dir = output_dir / "quotes"
    fieldnames = ["file", "source_id", "line_no", "translation", "raw_translation"]
    write_tsv(quotes_dir / "all_translated_dialogue.tsv", all_rows, fieldnames)
    write_tsv(quotes_dir / "setsuna_candidate_dialogue.tsv", candidate_rows, fieldnames)

    plain_lines = [row["translation"] for row in candidate_rows]
    (quotes_dir / "setsuna_candidate_dialogue.txt").write_text(
        "\n".join(plain_lines) + ("\n" if plain_lines else ""),
        encoding="utf-8",
    )

    summary = {
        "downloaded_files": len(listing),
        "all_dialogue_lines": len(all_rows),
        "setsuna_candidate_lines": len(candidate_rows),
        "candidate_prefixes": sorted(SETSUNA_FILE_PREFIXES),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default="wa2_special_corpus",
        help="directory to write downloaded files and extracted corpora",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir).resolve()
    build_corpus(output_dir)
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
