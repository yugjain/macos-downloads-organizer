#!/usr/bin/env python3
"""
macOS Downloads Organizer
=========================
A lightweight, autonomous background organizer for macOS ~/Downloads.
- Automatically organizes loose files into categorized folders.
- Supports custom regex/keyword rules and extension mappings.
- Safe: never overwrites files (auto-increments names), ignores in-progress downloads,
  and never touches existing subdirectories.
- Designed to run periodically via macOS launchd or manually via CLI.
"""

import json
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path

# Paths
DOWNLOADS_DIR = Path.home() / "Downloads"
CONFIG_FILE = Path.home() / ".config" / "downloads-organizer" / "config.json"
LOG_FILE = Path.home() / "Library" / "Logs" / "downloads-organizer.log"

# Setup Logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)

# Files currently being downloaded (must not be touched)
IN_PROGRESS_EXTS = {".crdownload", ".download", ".part", ".tmp"}

# Default Category Destinations
DEFAULT_CATEGORIES = {
    "screenshots": "Screenshots",
    "images": "Images",
    "documents": "Documents",
    "archives": "Archives",
    "installers": "Installers",
    "developer": "Developer & Code",
    "audio": "Audio & Music",
    "videos": "Videos",
    "books": "Books & Papers",
    "misc": "Other & Miscellaneous",
}

# Default Extension Mappings
DEFAULT_EXTENSIONS = {
    # Images
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".heic": "images",
    ".webp": "images",
    ".gif": "images",
    ".svg": "images",
    ".bmp": "images",
    ".tiff": "images",
    ".raw": "images",
    ".ico": "images",
    # Audio
    ".mp3": "audio",
    ".wav": "audio",
    ".aac": "audio",
    ".flac": "audio",
    ".m4a": "audio",
    ".ogg": "audio",
    ".wma": "audio",
    # Videos
    ".mp4": "videos",
    ".mov": "videos",
    ".mkv": "videos",
    ".avi": "videos",
    ".webm": "videos",
    ".m4v": "videos",
    # Archives
    ".zip": "archives",
    ".tar": "archives",
    ".gz": "archives",
    ".tgz": "archives",
    ".rar": "archives",
    ".7z": "archives",
    ".bz2": "archives",
    ".xz": "archives",
    # Installers
    ".dmg": "installers",
    ".pkg": "installers",
    ".iso": "installers",
    # Code & Data
    ".py": "developer",
    ".js": "developer",
    ".ts": "developer",
    ".jsx": "developer",
    ".tsx": "developer",
    ".sh": "developer",
    ".json": "developer",
    ".yml": "developer",
    ".yaml": "developer",
    ".xml": "developer",
    ".html": "developer",
    ".css": "developer",
    ".sql": "developer",
    ".db": "developer",
    ".sqlite": "developer",
    ".sqlite3": "developer",
    # Books / Academic
    ".epub": "books",
    ".mobi": "books",
    # Documents
    ".pdf": "documents",
    ".docx": "documents",
    ".doc": "documents",
    ".xlsx": "documents",
    ".xls": "documents",
    ".pptx": "documents",
    ".ppt": "documents",
    ".csv": "documents",
    ".txt": "documents",
}

def load_config() -> dict:
    """Load user configuration if present, otherwise return empty structure."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not read config file {CONFIG_FILE}: {e}")
    return {}

def get_unique_destination(dest_dir: Path, filename: str) -> Path:
    """Generate a collision-free destination path."""
    dest_path = dest_dir / filename
    if not dest_path.exists():
        return dest_path

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1

def determine_destination_folder(filename: str, existing_folders: set, config: dict) -> str:
    """Determine the destination folder name based on custom rules, patterns, and extensions."""
    lower = filename.lower()
    suffix = Path(filename).suffix.lower()

    if suffix in IN_PROGRESS_EXTS:
        return None

    # 1. Custom user regex rules from config.json
    custom_rules = config.get("rules", [])
    for rule in custom_rules:
        pattern = rule.get("pattern")
        folder = rule.get("folder")
        if pattern and folder:
            if re.search(pattern, lower, re.IGNORECASE):
                return folder

    # 2. Built-in pattern recognition
    # Screenshots
    if re.search(r"screencapture|screenshot|screen shot", lower):
        if "Screenshots" in existing_folders:
            return "Screenshots"
        return DEFAULT_CATEGORIES["screenshots"]

    # Invoices & Receipts
    if re.search(r"invoice|receipt|flipkart order|amazon order|\bbill\b", lower):
        if "Invoices, Purchases & Receipts" in existing_folders:
            return "Invoices, Purchases & Receipts"

    # Tax & Government identification
    if re.search(r"\btax\b|form 16|form-16|\bitr\b|\btds\b|ay 202[4-7]|pan card|aadhaar", lower):
        if "Tax, Government & Identification" in existing_folders:
            return "Tax, Government & Identification"

    # Resumes
    if re.search(r"resume|curriculum vitae|\bcv\b", lower):
        if "Resumes & Profiles" in existing_folders:
            return "Resumes & Profiles"
        elif "Resumes" in existing_folders:
            return "Resumes"

    # Banking & Financial statements
    if re.search(r"bank statement|iob bank|\bbank\b|passbook|investment", lower):
        if "Banking, Investments & Finance" in existing_folders:
            return "Banking, Investments & Finance"

    # Travel & Flights
    if re.search(r"visa|boarding pass|\bflight\b|itinerary|air ticket", lower):
        if "Travel, Flights & Visas" in existing_folders:
            return "Travel, Flights & Visas"

    # Work contracts / SOWs
    if re.search(r"nttd|ntt data|mulesoft.*sow|sow.*cts|\bsow\b", lower):
        if "NTT DATA SOWs - Yug Jain" in existing_folders:
            return "NTT DATA SOWs - Yug Jain"
        elif "Work Projects & Tech Contracts" in existing_folders:
            return "Work Projects & Tech Contracts"

    # 3. Extension-based mapping
    category_key = DEFAULT_EXTENSIONS.get(suffix)
    if category_key:
        # Match existing folder name variations if user already has them
        variations = {
            "images": ["Images & Photos", "Images", "Photos", "Pictures"],
            "audio": ["Audio & Music", "Music", "Audio"],
            "videos": ["Videos", "Movies"],
            "archives": ["Archives", "Backups & Archives", "Back up and archives Google Takeout", "Zips"],
            "installers": ["Installers", "DMGs", "Applications"],
            "developer": ["Developer & Tools", "Developer & Code", "Code", "Dev"],
            "books": ["Books & Academic Research Papers", "Books"],
            "documents": ["Documents", "Docs"],
        }
        for candidate in variations.get(category_key, []):
            if candidate in existing_folders:
                return candidate
        return DEFAULT_CATEGORIES.get(category_key, "Documents")

    # Fallback for unclassified files
    if "Other & Miscellaneous" in existing_folders:
        return "Other & Miscellaneous"
    return DEFAULT_CATEGORIES["misc"]

def organize(dry_run: bool = False):
    """Scan Downloads and route loose files into category folders."""
    if not DOWNLOADS_DIR.exists():
        logging.error(f"Downloads folder not found at {DOWNLOADS_DIR}")
        return

    entries = list(DOWNLOADS_DIR.iterdir())
    existing_folders = {e.name for e in entries if e.is_dir() and not e.name.startswith(".")}
    loose_files = [e for e in entries if e.is_file() and not e.name.startswith(".")]

    if not loose_files:
        logging.info("No loose files to organize in Downloads.")
        return

    config = load_config()
    now = time.time()
    moved_count = 0

    for file_path in loose_files:
        # Avoid files modified within last 15 seconds (likely still saving/downloading)
        try:
            mtime = file_path.stat().st_mtime
            if now - mtime < 15:
                logging.info(f"Skipping '{file_path.name}' (modified < 15s ago, may still be active)")
                continue
        except OSError:
            continue

        folder_name = determine_destination_folder(file_path.name, existing_folders, config)
        if not folder_name:
            continue

        target_dir = DOWNLOADS_DIR / folder_name
        dest_file_path = get_unique_destination(target_dir, file_path.name)

        if dry_run:
            status = "EXISTING" if folder_name in existing_folders else "CREATE"
            logging.info(f"[DRY RUN] '{file_path.name}' -> '{folder_name}/{dest_file_path.name}' [{status}]")
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            existing_folders.add(folder_name)
            shutil.move(str(file_path), str(dest_file_path))
            logging.info(f"Moved '{file_path.name}' -> '{folder_name}/{dest_file_path.name}'")
            moved_count += 1

    if dry_run:
        logging.info(f"Dry run complete. Evaluated {len(loose_files)} loose files.")
    else:
        logging.info(f"Organized {moved_count} loose files.")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    organize(dry_run=dry_run)
