#!/usr/bin/env sh
# Differential check, independent of any test suite: runs the original Metaphone and Bob's
# modernized versions (rebuilt from a run's recorded diffs) on the same inputs and compares
# every output, including exceptions.  Usage: targets/metaphone/differential/check.sh runs/<id>
set -e
RUN=${1:?usage: check.sh runs/<id>}
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(cd "$HERE/../../.." && pwd); WORK=$(mktemp -d)
python3 "$HERE/inputs.py" > "$WORK/inputs.txt"
python3 - "$ROOT/$RUN/state.json" "$ROOT/targets/metaphone" "$WORK" <<'PY'
import json, os, shutil, subprocess, sys
state, target, work = sys.argv[1:]
src = os.path.join(target, "src/main/java")
versions = {"original": None, **{m["step"]: m["diff"] for m in json.load(open(state))["modernizations"] if m.get("diff")}}
for name, diff in versions.items():
    d = os.path.join(work, "src", name); shutil.copytree(src, d)
    if diff:
        f = os.path.join(d, "org/apache/commons/codec/language/Metaphone.java")
        text = open(f).read()  # the Apache file has CRLF endings; diffs were made on LF text
        open(f, "w").write(text)
        p = os.path.join(work, name + ".patch"); open(p, "w").write(diff)
        subprocess.run(["patch", "-s", os.path.join(d, "org/apache/commons/codec/language/Metaphone.java"), p], check=True)
    open(os.path.join(work, "versions.txt"), "a").write(name + "\n")
PY
for v in $(cat "$WORK/versions.txt"); do
  javac -nowarn -d "$WORK/build/$v" $(find "$WORK/src/$v" -name '*.java') "$HERE/Run.java" 2>/dev/null
  java -cp "$WORK/build/$v" Run "$WORK/inputs.txt" "$WORK/out-$v.txt"
done
echo "$(wc -l < "$WORK/inputs.txt") inputs; original throws on $(grep -c EXC "$WORK/out-original.txt") of them"
for v in $(grep -v '^original$' "$WORK/versions.txt"); do
  echo "$v: $(diff "$WORK/out-original.txt" "$WORK/out-$v.txt" | grep -c '^<' || true) outputs differ from the original"
done
