# SC-memories
This repository contains scripts to download, organize, and view your Snapchat Memories locally. It provides a way to download your memories, generate thumbnails for videos, and create a browsable HTML gallery similar to Snapchat.

---

## Files Overview

### 1. `generate.py`

Downloads your Snapchat Memories based on a JSON file exported from Snapchat.

**Features:**
- Downloads images and videos from your Snapchat Memories.
- Retries failed downloads up to 5 times.
- Saves failed downloads to `failed.txt`.
- Supports the `--failed-only` flag to retry only the failed downloads.
- Organizes media into a `media` folder.
- Automatically generates `memories_gallery.html` to browse your media.

**Usage:**
```
python3 generate.py
```

**Flags:**
- `--failed-only`: Only retry downloads listed in `failed.txt`.

---

### 2. `gen_thumbnails.py`

Generates thumbnails for your video files for faster preview in the gallery.

**Requirements:**
- `ffmpeg` installed and accessible in your system PATH.  
  ([Download ffmpeg](https://ffmpeg.org/download.html))

**Usage:**
```
python gen_thumbnails.py
```

This will create a `thumbnails` folder and generate a `.jpg` thumbnail for each video in the `media` folder.

---

### 3. `gen_html.py`

Generates a browsable HTML gallery from your existing media and thumbnails.

**Features:**
- Automatically detects images and videos in the `media` folder.
- Uses thumbnails for videos if available.
- Lightbox view for images and videos with next/previous buttons.
- Keyboard navigation: ArrowLeft, ArrowRight, Escape.
- Pauses videos when switching or closing to prevent overlapping audio.
- Sorts media in reverse chronological order by month.
- Labels each thumbnail as `Picture` or `Video`.

**Usage:**
```
python gen_html.py
```

---

## Getting Your Snapchat Data

To use these scripts, you need to export your Snapchat Memories:

1. Open Snapchat and go to **Settings → My Data**.
2. Request your Memories and select **JSON formatting**.
3. Snapchat will email you a link to download a ZIP file containing your memories.
4. Unzip the ZIP file you downloaded from Snapchat.
5. Move `memories_history.json` into the same folder as `generate.py`.

---

## Recommended Workflow

1. Download your Snapchat data and place `memories_history.json` next to `generate.py`.
2. Run `generate.py` to download all media using `python3 generate.py`.
3. Run `gen_thumbnails.py` to generate video thumbnails.
4. Run `gen_html.py` to create the HTML gallery (`memories_gallery.html`).
5. Open `memories_gallery.html` in a web browser to view your Memories.

---

## Notes

- Make sure all scripts are in the same folder for simplicity.
- `gen_html.py` and `generate.py` can work independently; `gen_html.py` does not require re-downloading media.
- For videos, make sure thumbnails exist for proper gallery previews. Missing thumbnails will be logged in the console.

