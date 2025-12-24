#!/usr/bin/env python3
import re
import calendar
from pathlib import Path
from collections import defaultdict
from datetime import datetime

MEDIA_DIR_NAME = "media"
THUMB_DIR_NAME = "thumbnails"
VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]

# -------------------- LOGGING --------------------
def log(msg):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode(), flush=True)

# -------------------- PARSE FILENAME --------------------
def parse_datetime_from_filename(filename):
    base = filename.rsplit('.', 1)[0]
    match = re.match(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', base)
    if not match:
        return None
    year, month, day, hour, minute, second = map(int, match.groups())
    return datetime(year, month, day, hour, minute, second)

# -------------------- BUILD GALLERY --------------------
def build_gallery_index(media_dir: Path, thumb_dir: Path):
    items = []
    thumb_dir.mkdir(exist_ok=True)

    for path in media_dir.iterdir():
        if not path.is_file():
            continue

        dt = parse_datetime_from_filename(path.name)
        if dt is None:
            log(f"Skipping file (invalid name format): {path.name}")
            continue

        ext = path.suffix.lower()
        is_video = ext in VIDEO_EXTENSIONS

        thumb_path = None
        if is_video:
            thumb_path = thumb_dir / f"{path.stem}.jpg"
            if not thumb_path.exists():
                log(f"Thumbnail missing for video: {path.name}. Please generate with ffmpeg.")
        else:
            thumb_path = path

        items.append({
            "path": str(path).replace("\\","/"),
            "thumb": str(thumb_path).replace("\\","/"),
            "datetime": dt,
            "year": dt.year,
            "month": dt.month,
            "month_name": calendar.month_name[dt.month],
            "is_video": is_video
        })

    return items

# -------------------- BUILD HTML --------------------
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
.card{background:#000;border-radius:8px;overflow:hidden;cursor:pointer;position:relative}
.card-label{position:absolute;bottom:4px;left:4px;background:rgba(0,0,0,0.6);color:#eaeaf0;font-size:12px;padding:2px 4px;border-radius:4px}
img,video{width:100%;height:100%;object-fit:cover}
.hidden{display:none}
#lightbox{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);display:none;align-items:center;justify-content:center;z-index:1000;flex-direction:column}
#lightbox img, #lightbox video{max-width:90%;max-height:80%;margin-bottom:16px}
#lightbox button{background:#181b21;color:#eaeaf0;border:none;padding:8px 16px;margin:4px;font-size:16px;cursor:pointer;border-radius:6px}
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
            items_m = sorted(grouped[year][month], key=lambda x: x["datetime"], reverse=True)
            html += f'''
<div class="month">
  <div class="month-header" onclick="this.nextElementSibling.classList.toggle('hidden')">
    <strong>{calendar.month_name[month]}</strong>
    <span>{len(items_m)}</span>
  </div>
  <div class="grid">
'''
            for i, item in enumerate(items_m):
                html += f'<div class="card" data-index="{i}" data-type="{"video" if item["is_video"] else "image"}" data-path="{item["path"]}">'
                html += f'<img src="{item["thumb"]}">'
                html += f'<div class="card-label">{"Video" if item["is_video"] else "Picture"}</div>'
                html += '</div>'
            html += "</div></div>"
        html += "</section>"

    html += """
<div id="lightbox">
  <div id="lightbox-content"></div>
  <div>
    <button id="prevBtn">Previous</button>
    <button id="nextBtn">Next</button>
    <button id="closeBtn">Close</button>
  </div>
</div>

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

let lightbox=document.getElementById('lightbox');
let lightboxContent=document.getElementById('lightbox-content');
let cards=document.querySelectorAll('.card');
let currentIndex=0;
let currentCards=Array.from(cards);

function showLightbox(index){
  const prevVideo = lightboxContent.querySelector('video');
  if(prevVideo){ prevVideo.pause(); prevVideo.currentTime=0; }

  currentIndex=index;
  const card=currentCards[currentIndex];
  lightboxContent.innerHTML='';
  const type=card.dataset.type;
  const path=card.dataset.path;

  if(type==="image"){
    let img=document.createElement('img');
    img.src=path;
    lightboxContent.appendChild(img);
  } else {
    let vid=document.createElement('video');
    vid.src=path;
    vid.controls=true;
    vid.autoplay=true;
    lightboxContent.appendChild(vid);
  }
  lightbox.style.display='flex';
}

cards.forEach((card,i)=>card.onclick=()=>showLightbox(i));

document.getElementById('nextBtn').onclick=()=>{ showLightbox((currentIndex+1)%currentCards.length); };
document.getElementById('prevBtn').onclick=()=>{ showLightbox((currentIndex-1+currentCards.length)%currentCards.length); };

document.getElementById('closeBtn').onclick=()=>{
  const video = lightboxContent.querySelector('video');
  if(video){ video.pause(); video.currentTime=0; }
  lightbox.style.display='none';
};

document.addEventListener('keydown', function(e){
  if(lightbox.style.display==='flex'){
    if(e.key==='ArrowRight'){document.getElementById('nextBtn').click();}
    if(e.key==='ArrowLeft'){document.getElementById('prevBtn').click();}
    if(e.key==='Escape'){
        const video = lightboxContent.querySelector('video');
        if(video){ video.pause(); video.currentTime=0; }
        document.getElementById('closeBtn').click();
    }
  }
});
</script>

</body></html>
"""
    return html

# -------------------- MAIN --------------------
def main():
    media_dir = Path(MEDIA_DIR_NAME)
    thumb_dir = Path(THUMB_DIR_NAME)
    if not media_dir.exists():
        log(f"ERROR: Media folder '{MEDIA_DIR_NAME}' not found")
        return

    gallery_items = build_gallery_index(media_dir, thumb_dir)
    html = build_html(gallery_items)

    output_path = Path("memories_gallery.html")
    output_path.write_text(html, encoding="utf-8")

    log(f"Gallery generated at: {output_path.resolve()}")
    log(f"Media files indexed: {len(gallery_items)}")
    log("Done")

if __name__ == "__main__":
    main()
