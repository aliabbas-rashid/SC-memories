#!/usr/bin/env python3
import json
import sys
import time
import argparse
import calendar
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from urllib.request import urlopen, Request

MAX_RETRIES = 5
MEDIA_DIR_NAME = "media"
FAILED_FILE = "failed.txt"


# -------------------- LOGGING --------------------

def log(msg):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore").decode(), flush=True)


# -------------------- LOAD MEMORIES --------------------

def load_memories(json_path: Path):
    with json_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    memories = []

    for item in raw:
        try:
            date_str = item.get("Date") or item.get("Create Time") or item.get("Creation Time")
            filename = item.get("Filename") or item.get("File Name")
            url = item.get("Download Link") or item.get("Download URL")
            media_type = item.get("Media Type", "")

            if not (date_str and filename and url):
                continue

            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            memories.append({
                "filename": filename,
                "url": url,
                "datetime": dt,
                "media_type": media_type.lower()
            })
        except Exception:
            continue

    return memories


# -------------------- DOWNLOAD --------------------

def download_file(url, dest: Path):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as r, dest.open("wb") as f:
        f.write(r.read())


def download_media_files(memories, output_dir: Path, failed_only=False):
    media_dir = output_dir / MEDIA_DIR_NAME
    media_dir.mkdir(exist_ok=True)

    failures = []
    downloaded = 0

    failed_map = {}
    if failed_only and Path(FAILED_FILE).exists():
        with open(FAILED_FILE, "r", encoding="utf-8") as f:
            for line in f:
                name, url = line.strip().split("|", 1)
                failed_map[name] = url

    for idx, item in enumerate(memories, 1):
        filename = item["filename"]
        url = item["url"]

        if failed_only and filename not in failed_map:
            continue

        dest = media_dir / filename
        if dest.exists():
            continue

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                log(f"[{idx}/{len(memories)}] {filename} (attempt {attempt})")
                download_file(url, dest)
                downloaded += 1
                success = True
                break
            except Exception as e:
                log(f"  retry failed: {e}")
                time.sleep(1)

        if not success:
            failures.append((filename, url))

    if failures:
        with open(FAILED_FILE, "w", encoding="utf-8") as f:
            for name, url in failures:
                f.write(f"{name}|{url}\n")
        log(f"ERROR: {len(failures)} files failed after {MAX_RETRIES} retries")
    else:
        if Path(FAILED_FILE).exists():
            Path(FAILED_FILE).unlink()
        log("All files downloaded successfully")

    return downloaded


# -------------------- GALLERY --------------------

def build_gallery_index(memories, media_dir: Path):
    items = []

    for item in memories:
        path = media_dir / item["filename"]
        if not path.exists():
            continue

        items.append({
            "path": f"{MEDIA_DIR_NAME}/{item['filename']}",
            "year": item["datetime"].year,
            "month": item["datetime"].month,
            "month_name": calendar.month_name[item["datetime"].month],
            "is_video": "video" in item["media_type"]
        })

    return items


def build_html(items):
    grouped = defaultdict(lambda: defaultdict(list))
    for i in items:
        grouped[i["year"]][i["month"]].append(i)

    years = sorted(grouped.keys(), reverse=True)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Snapchat Memories</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body{margin:0;font-family:system-ui;background:#0f1115;color:#eaeaf0}
header{padding:16px;position:sticky;top:0;background:#0f1115cc;backdrop-filter:blur(6px)}
select{background:#181b21;color:#eaeaf0;border:1px solid #2a2f3a;border-radius:6px;padding:6px}
.year{padding:16px}
.month{margin-bottom:14px}
.month-header{cursor:pointer;padding:10px;background:#181b21;border-radius:8px;display:flex;justify-content:space-between}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:8px}
.card{background:#000;border-radius:8px;overflow:hidden}
img,video{width:100%;height:100%;object-fit:cover}
.hidden{display:none}
</style>
</head>
<body>

<header>
  <h2>Snapchat Memories</h2>
  <select id="yearFilter"><option value="all">All years</option></select>
</header>
"""

    for year in years:
        html += f'<section class="year" data-year="{year}"><h3>{year}</h3>'
        for month in sorted(grouped[year].keys(), reverse=True):
            items_m = grouped[year][month]
            html += f'''
<div class="month">
  <div class="month-header" onclick="this.nextElementSibling.classList.toggle('hidden')">
    <strong>{calendar.month_name[month]}</strong>
    <span>{len(items_m)}</span>
  </div>
  <div class="grid">
'''
            for i in items_m:
                if i["is_video"]:
                    html += f'<div class="card"><video src="{i["path"]}" controls preload="metadata"></video></div>'
                else:
                    html += f'<div class="card"><img src="{i["path"]}" loading="lazy"></div>'
            html += "</div></div>"
        html += "</section>"

    html += """
<script>
const years=document.querySelectorAll(".year");
const sel=document.getElementById("yearFilter");
years.forEach(y=>{
 let o=document.createElement("option");
 o.value=y.dataset.year;o.textContent=y.dataset.year;sel.appendChild(o);
});
sel.onchange=()=>years.forEach(y=>{
 y.style.display=sel.value==="all"||y.dataset.year===sel.value?"block":"none";
});
</script>

</body></html>
"""
    return html


# -------------------- MAIN --------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--failed-only", action="store_true")
    args = parser.parse_args()

    json_path = Path("memories_history.json")
    if not json_path.exists():
        log("ERROR: memories_history.json not found")
        sys.exit(1)

    output_dir = json_path.parent
    media_dir = output_dir / MEDIA_DIR_NAME

    memories = load_memories(json_path)
    log(f"Loaded {len(memories)} memories")

    download_media_files(memories, output_dir, args.failed_only)

    gallery_items = build_gallery_index(memories, media_dir)
    html = build_html(gallery_items)

    output_path = output_dir / "memories_gallery.html"
    output_path.write_text(html, encoding="utf-8")

    log(f"Gallery generated at: {output_path.resolve()}")
    log(f"Media files indexed: {len(gallery_items)}")
    log("Done")


if __name__ == "__main__":
    main()
