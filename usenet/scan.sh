#!/bin/bash
# scan.sh <hierarchy-item> <group>   e.g. scan.sh usenet-soc soc.motss
set -u
D=/tmp/claude-0/-home-user-devinendorphins-dextromethorphan-archaive/1867aab3-9062-534a-a3a3-6d33bd4cfcec/scratchpad
ITEM=$1; G=$2
cd "$D" || exit 1
OUT="$D/results/$G.txt"; mkdir -p "$D/results"
echo "=== GROUP: $G  (item $ITEM)" | tee "$OUT"
rm -f w.zip; rm -f "$G.mbox"
curl -sL --max-time 3000 -o w.zip "https://archive.org/download/$ITEM/$G.mbox.zip" || { echo "DOWNLOAD FAIL" | tee -a "$OUT"; exit 1; }
echo "zip bytes: $(stat -c%s w.zip)" | tee -a "$OUT"
unzip -o -q w.zip 2>/dev/null
MB=$(ls -S *.mbox 2>/dev/null | head -1)
[ -z "$MB" ] && { echo "NO MBOX EXTRACTED" | tee -a "$OUT"; exit 1; }
echo "mbox: $MB  $(stat -c%s "$MB") bytes" | tee -a "$OUT"
echo "--- total messages (From_ lines):" | tee -a "$OUT"
grep -ac "^From " "$MB" | tee -a "$OUT"
echo "--- year histogram:" | tee -a "$OUT"
grep -ao "^Date: .*" "$MB" | grep -ao "\b19[89][0-9]\b\|\b20[0-2][0-9]\b" | sort | uniq -c | sort -k2 | tee -a "$OUT"
echo "--- KEY COUNTS:" | tee -a "$OUT"
for k in "YGXS04" "Gallegos" "Devon Gallegos" "@prodigy\.com" "@prodigy\.net"; do
  printf "%-20s %s\n" "$k" "$(grep -aic "$k" "$MB")" | tee -a "$OUT"
done
echo "--- HITS (YGXS04):" | tee -a "$OUT"
grep -ain "YGXS04" "$MB" | head -40 | tee -a "$OUT"
echo "--- HITS (Gallegos, with line numbers):" | tee -a "$OUT"
grep -ain "Gallegos" "$MB" | head -60 | tee -a "$OUT"
rm -f w.zip "$MB" *.mbox
echo "=== done $G" | tee -a "$OUT"
