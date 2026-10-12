#!/usr/bin/env bash
# Copies the committed files to the server and (re)starts the dashboard.
# Run from this folder: ./deploy.sh
set -euo pipefail
SERVER=aaravmodi@100.76.57.23
DIR=projects/home-dashboard

if [ -n "$(git status --porcelain)" ]; then
  echo "Commit your changes first: only committed files are deployed." >&2
  exit 1
fi
ssh -o BatchMode=yes "$SERVER" "mkdir -p $DIR"
git archive HEAD | ssh -o BatchMode=yes "$SERVER" "tar -x -C $DIR"
ssh -o BatchMode=yes "$SERVER" "cd $DIR && docker compose up -d --remove-orphans"
for _ in $(seq 1 20); do
  if curl -fs -m 5 -o /dev/null http://100.76.57.23/; then
    echo "Live: http://100.76.57.23 ($(git log -1 --format='%h %s'))"
    exit 0
  fi
  sleep 3
done
echo "Deployed, but the page isn't answering yet. Check: ssh $SERVER 'cd $DIR && docker compose logs'" >&2
exit 1
