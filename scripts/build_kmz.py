#!/usr/bin/env python3
import glob, os, subprocess, sys

DATA_DIR = "data"
OUT_DIR = "build"

os.makedirs(OUT_DIR, exist_ok=True)

gsbs = sorted(glob.glob(os.path.join(DATA_DIR, "*.gsb")))
if not gsbs:
    print("No .gsb files found in data/. Add your grids to data/ and rerun.", file=sys.stderr)
    sys.exit(1)

cmd_base = [sys.executable, "src/gsb_to_kmz.py"]
for g in gsbs:
    base = os.path.splitext(os.path.basename(g))[0]
    out = os.path.join(OUT_DIR, f"{base}_coverage.kmz")
    print(f"Processing {g} -> {out}")
    subprocess.check_call(cmd_base + ["--input", g, "--out", out, "--name", f"{base} Coverage"])

print("Done.")
