#!/usr/bin/env python3
import argparse
import os
from osgeo import gdal
import simplekml
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union

def extent_from_ds(ds):
    gt = ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    minx = gt[0]
    maxy = gt[3]
    maxx = minx + gt[1]*cols
    miny = maxy + gt[5]*rows
    # Ensure (lon,lat) order for KML; close the ring by repeating the first coord
    ring = [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)]
    return ring

def write_kmz(polygons, out_path, name="GSB Coverage"):
    kml = simplekml.Kml()
    folder = kml.newfolder(name=name)
    for i, poly in enumerate(polygons, start=1):
        if isinstance(poly, Polygon):
            geoms = [poly]
            label = f"Subgrid {i}"
        elif hasattr(poly, "geoms"):
            geoms = poly.geoms
            label = f"Merged Part {i}"
        else:
            continue

        for j, g in enumerate(geoms, start=1):
            coords = list(g.exterior.coords)
            pol = folder.newpolygon(name=f"{label} - {j}")
            pol.outerboundaryis = [(x, y, 0) for x, y in coords]  # KML expects (lon,lat,alt)
            pol.style.polystyle.fill = 1
            pol.style.polystyle.outline = 1
            pol.style.polystyle.color = "7d00ff00"  # semi-transparent green

    kml.savekmz(out_path)

def main():
    ap = argparse.ArgumentParser(description="Convert NTv2 .gsb coverage to KMZ closed polygons")
    ap.add_argument("--input", required=True, help="Path to .gsb file")
    ap.add_argument("--out", required=True, help="Output KMZ path")
    ap.add_argument("--name", default=None, help="Overlay name")
    args = ap.parse_args()

    gdal.UseExceptions()
    ds = gdal.Open(args.input)
    if ds is None:
        raise RuntimeError(f"Failed to open {args.input} as GDAL dataset")

    # Collect polygons from main dataset and subdatasets (if any)
    polygons = []
    # If the main dataset is a valid raster, add its extent
    try:
        ring = extent_from_ds(ds)
        polygons.append(Polygon(ring))
    except Exception:
        pass

    subdatasets = ds.GetSubDatasets() or []
    for (sub_name, sub_desc) in subdatasets:
        sds = gdal.Open(sub_name)
        if sds:
            ring = extent_from_ds(sds)
            polygons.append(Polygon(ring))

    if not polygons:
        raise RuntimeError("No extents could be derived (dataset or subdatasets missing geotransform).")

    # Write per-subgrid coverage
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    write_kmz(polygons, args.out, name=args.name or os.path.basename(args.input) + " Coverage")

    # Also write merged union next to it
    merged = unary_union(polygons)
    base, ext = os.path.splitext(args.out)
    merged_out = base.replace("_coverage", "") + "_merged.kmz"
    write_kmz([merged], merged_out, name=(args.name or os.path.basename(args.input)) + " (Merged)")

    print(f"Wrote: {args.out}")
    print(f"Wrote: {merged_out}")

if __name__ == "__main__":
    main()
