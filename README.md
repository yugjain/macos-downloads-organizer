# 📁 macOS Downloads Organizer

> A lightweight, zero-dependency background automation that keeps your Mac's `~/Downloads` folder permanently tidy and organized.

[![macOS Compatible](https://img.shields.io/badge/macOS-Sonoma%20%7C%20Ventura%20%7C%20Sequoia-black?logo=apple)](https://apple.com)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-none%20(stdlib)-brightgreen)]()

No paid utilities like Hazel, no clunky third-party apps, and zero RAM overhead. Runs natively in the background via macOS `launchd`.

---

## ✨ Features

* **Intelligent File Sorting:** Automatically files loose downloads into clear, categorized folders:
  * 📸 **Screenshots:** Automatically detects macOS screencaptures (`screencapture-*`, `Screenshot*`) $\rightarrow$ `Screenshots/`
  * 🖼️ **Images:** `.png`, `.jpg`, `.jpeg`, `.heic`, `.webp`, `.svg`, `.gif` $\rightarrow$ `Images/`
  * 📄 **Documents:** `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.txt`, `.csv` $\rightarrow$ `Documents/`
  * 📦 **Archives:** `.zip`, `.tar.gz`, `.7z`, `.rar`, `.gz` $\rightarrow$ `Archives/`
  * 💾 **Installers:** `.dmg`, `.pkg`, `.iso` $\rightarrow$ `Installers/`
  * 💻 **Developer & Code:** `.py`, `.js`, `.ts`, `.json`, `.sql`, `.db`, `.sh`, `.yaml` $\rightarrow$ `Developer & Code/`
  * 🎵 **Audio & Media:** `.mp3`, `.wav`, `.mp4`, `.mov`, `.mkv` $\rightarrow$ `Audio & Music/` or `Videos/`
* **Respects Existing Folders:** If you already have existing folders (e.g. `Images & Photos` or `Resumes & Profiles`), it smartly routes files into them rather than creating duplicates.
* **100% Non-Destructive & Safe:**
  * **Zero Overwrites:** If a file with the same name exists, it generates `filename (1).ext`.
  * **In-Progress Protection:** Automatically ignores `.crdownload`, `.download`, `.part`, `.tmp` and files modified in the last 15 seconds.
  * **Never Moves Subdirectories:** Only organizes loose files at the root of `~/Downloads`.
* **Configurable:** Define custom keyword patterns (e.g., invoices, employer SOWs, tax forms) via a simple `config.json`.

---

## ⚡ Quick Start

### 1. Clone & Install
Open your Mac's Terminal and run:

```zsh
git clone https://github.com/yugjain/macos-downloads-organizer.git
cd macos-downloads-organizer
chmod +x install.sh
./install.sh
```

The installer will:
1. Place the organizer script in `~/.local/bin/organize_downloads.py`.
2. Create and load a background LaunchAgent (`~/Library/LaunchAgents/com.$USER.downloads.organizer.plist`) that runs automatically **every hour** and upon system login.
3. Automatically launch your macOS **Full Disk Access** settings page.

---

### 2. 🔐 Grant Full Disk Access (Required by macOS)
Because Apple strictly locks down `~/Downloads` for background daemons:

1. In **System Settings → Privacy & Security → Full Disk Access**:
2. Click the **`+`** icon (authenticate with Touch ID / password).
3. Press **<kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>G</kbd>**, paste your Python executable path:
   ```text
   /Library/Developer/CommandLineTools/usr/bin/python3
   ```
   *(Or `/opt/homebrew/bin/python3` if using Homebrew Python)*.
4. Click **Open** and toggle it **ON**.

---

## 🛠️ Manual Usage & Dry Run

You can run the script manually at any time or test what it would do before moving anything:

```zsh
# Preview what would be organized without moving files
python3 ~/.local/bin/organize_downloads.py --dry-run

# Run manual cleanup immediately
python3 ~/.local/bin/organize_downloads.py

# View live background activity logs
tail -f ~/Library/Logs/downloads-organizer.log
```

---

## ⚙️ Custom Rules (`config.json`)

Want specific files sorted into custom folders? (e.g. invoices, tax files, work project docs).

Copy `config.example.json` to `~/.config/downloads-organizer/config.json`:

```zsh
mkdir -p ~/.config/downloads-organizer
cp config.example.json ~/.config/downloads-organizer/config.json
```

Edit `~/.config/downloads-organizer/config.json`:
```json
{
  "rules": [
    {
      "pattern": "invoice|receipt|order",
      "folder": "Invoices & Receipts"
    },
    {
      "pattern": "tax|form-16|itr|w2",
      "folder": "Taxes & Financial"
    },
    {
      "pattern": "myproject.*sow|contract",
      "folder": "Work Projects"
    }
  ]
}
```

---

## 🗑️ Uninstallation

To remove the background automation completely:

```zsh
cd macos-downloads-organizer
./uninstall.sh
```
*(Your categorized folders in `~/Downloads` remain untouched).*

---

## 📄 License
Released under the [MIT License](LICENSE).
