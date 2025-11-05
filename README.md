# NTv2 **.gsb** Coverage → **KMZ** (Google Earth) Converter

This repo turns one or more **NTv2 grid shift** files (`.gsb`) into **closed polygon** overlays
you can open in **Google Earth** (`.kmz`). It extracts the geographic coverage (bounding polygon)
for each grid/subgrid and writes a properly **closed polygon** per subgrid, plus an optional
**merged coverage** polygon.

> No ArcGIS required. Uses GDAL in a GitHub Action so you can just push a `.gsb` and download the KMZ artifact.

---

## Quick start (GitHub-only, zero local setup)

1. Put your `.gsb` file(s) in the `data/` folder.
2. Commit and push.
3. GitHub Actions automatically builds KMZ(s) and uploads them as **workflow artifacts**.
4. Download the `kmz-artifacts.zip` from the workflow run page. It will contain:
   - `<gridname>_coverage.kmz` — polygons per subgrid (closed rings).
   - `<gridname>_merged.kmz` — unioned coverage (single polygon or multipolygon).

> Works great for Toronto/Ontario grids like `TO27CSv1.gsb`, `ON27CSv1.gsb`, etc.

---

## Local usage (optional)

> You need GDAL installed locally. If that’s annoying, just use the GitHub Action.

```bash
# 1) Install deps (Linux example with system GDAL)
python -m venv .venv && source .venv/bin/activate
pip install simplekml shapely
# Install GDAL matching your system; e.g. using apt:
#   sudo apt-get update && sudo apt-get install -y gdal-bin libgdal-dev
#   pip install "GDAL==$(gdal-config --version).*"

# 2) Convert one file
python src/gsb_to_kmz.py --input data/TO27CSv1.gsb --out build/TO27CSv1_coverage.kmz --name "TO27CSv1 Coverage"

# 3) Batch convert everything in data/
python scripts/build_kmz.py
```

Output KMZ files open directly in **Google Earth** (desktop).

---

## What the script does

- Opens the `.gsb` with **GDAL**.
- Detects **subgrids** (if any). Each subgrid gets a rectangle polygon from its pixel geotransform.
- Writes **closed** polygon rings in KML/KMZ (longitude/latitude order).
- Also computes a **merged union** polygon across all subgrids (via **shapely**).

If your `.gsb` has multiple disjoint subgrids, you’ll get multiple rectangles in the coverage output,
and a merged multipolygon in the merged KMZ.

---

## Files

- `src/gsb_to_kmz.py` – Core script/CLI.
- `scripts/build_kmz.py` – Batch builder used by CI; processes all `.gsb` in `data/`.
- `.github/workflows/build.yml` – CI that installs GDAL and publishes artifacts.
- `data/` – Put your `.gsb` files here.
- `build/` – Output directory (CI creates and fills it).

---

## License

MIT
