#!/usr/bin/env bash
# Back up this laptop's projects and Notepad notes to the home server.
#   bash laptop-backup/backup.sh            (from Git Bash)
#
# Server, under ~/backups/laptop/:
#   projects/          a copy of Documents/Projects, replaced each run
#   notepad/latest/    Notepad's tabs (raw/) and their text (text/)
#   notepad/<date>/    each run's notes, kept, since they're tiny
#
# Left out: the Upside Robotics folders in not-backed-up.txt, and folders that are
# rebuilt from the project files (node_modules, Python environments, caches).
set -uo pipefail
here=$(cd "$(dirname "$0")" && pwd)
SERVER=${SERVER:-aaravmodi@100.76.57.23}
DEST=backups/laptop
PROJECTS="$USERPROFILE/Documents/Projects"
today=$(date +%Y-%m-%d)

skip=(--exclude=node_modules --exclude='.venv*' --exclude=venv --exclude=.browser-use-venv
      --exclude=__pycache__ --exclude=.next --exclude=.pytest_cache --exclude=.ruff_cache
      --exclude=.mypy_cache)
while IFS= read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  skip+=(--exclude="./$line")
done < "$here/not-backed-up.txt"

echo "Notepad notes..."
stage=$(mktemp -d)
python "$here/notepad_notes.py" "$stage" || exit 1
tar -C "$stage" -cf - . | ssh -o BatchMode=yes "$SERVER" \
  "set -e; mkdir -p $DEST/notepad/$today && tar -xf - -C $DEST/notepad/$today \
   && rm -rf $DEST/notepad/latest && cp -r $DEST/notepad/$today $DEST/notepad/latest"
rm -rf "$stage"

echo "Projects (about 7 GB the first time; this takes a while over Wi-Fi)..."
ssh -o BatchMode=yes "$SERVER" "rm -rf $DEST/projects.new && mkdir -p $DEST/projects.new"
tar -C "$PROJECTS" -cf - "${skip[@]}" . \
  | ssh -o BatchMode=yes "$SERVER" "tar -xf - -C $DEST/projects.new"
statuses=("${PIPESTATUS[@]}")
# tar exits 1 for "file changed as we read it" (a file being written); the copy is still good.
if (( statuses[0] > 1 || statuses[1] != 0 )); then
  echo "The projects copy failed (tar ${statuses[0]}, server ${statuses[1]}); the last backup is untouched." >&2
  exit 1
fi
ssh -o BatchMode=yes "$SERVER" \
  "rm -rf $DEST/projects && mv $DEST/projects.new $DEST/projects && du -sh $DEST/projects $DEST/notepad"
echo "Backed up to $SERVER:~/$DEST ($(date '+%a %b %d %I:%M %p'))"
