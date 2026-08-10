#!/bin/bash
D=/tmp/claude-0/-home-user-devinendorphins-dextromethorphan-archaive/1867aab3-9062-534a-a3a3-6d33bd4cfcec/scratchpad
cd "$D" || exit 1
INV="$D/prodigy_ids.tsv"
for spec in "$@"; do
  ITEM=${spec%%:*}; G=${spec##*:}
  rm -f w2.zip *.mbox
  curl -sL --max-time 3000 -o w2.zip "https://archive.org/download/$ITEM/$G.mbox.zip" || continue
  unzip -o -q w2.zip 2>/dev/null
  MB=$(ls -S *.mbox 2>/dev/null | head -1)
  [ -z "$MB" ] && continue
  # every address-like prodigy.com token, with the paren name when present
  grep -aoiE "[A-Za-z0-9]{4,8}@prodigy\.(com|net)( \([^)]{0,60}\))?" "$MB" \
    | sed "s|^|$G\t|" >> "$INV"
  echo "done $G ($(wc -l < "$INV") cumulative)" >&2
  rm -f w2.zip "$MB" *.mbox
done
