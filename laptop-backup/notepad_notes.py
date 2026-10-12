"""Copy Notepad's open tabs, saved and unsaved, into a folder, plus a readable .txt of each.

Windows 11 Notepad keeps every open tab, including ones never saved, as binary files in
its app folder. The raw files are copied as they are (so they can be put back), and the
text of each tab is pulled out into text/ so the notes can be read on the server.

Notes about Upside Robotics work are left out entirely (text and raw files) and listed.

    python notepad_notes.py <output folder>
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

STATE = Path.home() / "AppData/Local/Packages/Microsoft.WindowsNotepad_8wekyb3d8bbwe/LocalState"
# Words that mark a note as Upside work; those notes aren't copied.
WORK_WORDS = re.compile(
    r"upside|robot|planter|base station|prescription|field tour|teleop|performance-board"
    r"|\bshap\b|rain sensor|\bfarm|\bgdd\b|\bfields?\b",
    re.IGNORECASE,
)


def _decode(data: bytes) -> str:
    text = data.decode("utf-16-le", errors="replace")
    runs = re.findall(r"[^\x00-\x08\x0b\x0c\x0e-\x1f\ufffd]{6,}", text)
    # Header bytes decode as stray letters around the text ("P㴁C:\\Users...Ā"), so each
    # run starts at its first three plain characters and drops any odd ones at the end.
    runs = [re.sub(r"^.*?(?=[\x20-\x7e]{3})", "", run, flags=re.S) for run in runs]
    runs = [re.sub(r"[^\x20-\x7e\s]+$", "", run) for run in runs]
    lines = (run.replace("\r\n", "\n").replace("\r", "\n").strip() for run in runs)
    return "\n".join(line for line in lines if len(line) >= 3)


def tab_text(data: bytes) -> str:
    """The readable text in a tab file: its UTF-16 runs, without the binary header.

    The header's length can be odd, so the text starts on either byte. Read from the wrong
    one, English comes out as CJK-looking characters, so the right reading is the one with
    more plain ASCII.
    """
    readings = [_decode(data[start:]) for start in (0, 1)]
    return max(readings, key=lambda text: len(re.findall(r"[\x20-\x7e]", text)))


def work_folders() -> re.Pattern[str]:
    """Paths into the Upside project folders listed in not-backed-up.txt."""
    listed = Path(__file__).with_name("not-backed-up.txt").read_text(encoding="utf-8")
    names = [line.strip() for line in listed.splitlines() if line.strip() and line[0] != "#"]
    # "upside-gis" was once "upside gis": match either spacing.
    alternatives = "|".join(re.escape(name).replace(r"\-", "[- ]").replace(r"\ ", "[- ]")
                            for name in names)
    return re.compile(rf"Projects\\(?:{alternatives})(?:\\|$)", re.IGNORECASE)


def slug(text: str) -> str:
    first = next((line for line in text.splitlines() if line.strip()), "note")
    return re.sub(r"[^A-Za-z0-9]+", "-", first).strip("-")[:50] or "note"


def main(out: Path) -> None:
    if not STATE.exists():
        print("Notepad has no saved tabs on this computer.")
        return
    (out / "text").mkdir(parents=True, exist_ok=True)
    in_work_folder = work_folders()
    work_tabs: set[str] = set()
    skipped: list[str] = []
    count = 0
    for tab in sorted((STATE / "TabState").glob("*.bin")):
        if re.search(r"\.\d\.bin$", tab.name):  # a tab's state files, not its content
            continue
        text = tab_text(tab.read_bytes())
        if len(text) < 3:
            continue
        when = datetime.fromtimestamp(tab.stat().st_mtime).strftime("%Y-%m-%d")
        name = f"{when}-{slug(text)}.txt"
        if WORK_WORDS.search(text) or in_work_folder.search(text):
            work_tabs.add(tab.name.split(".")[0])
            skipped.append(name)
            continue
        (out / "text" / name).write_text(text + "\n", encoding="utf-8")
        count += 1
    # The raw tab files too, minus the work notes' (<id>.bin, <id>.0.bin and <id>.1.bin).
    shutil.copytree(
        STATE,
        out / "raw",
        dirs_exist_ok=True,
        ignore=lambda _folder, names: [n for n in names if n.split(".")[0] in work_tabs],
    )
    print(f"Notepad: {count} notes backed up")
    for name in skipped:
        print(f"  left out (work): {name}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
