#!/usr/bin/env python3
"""
Drill collar calculator for R1.

Give it a surface target (where the vein / anomaly crops out), the structure's dip and dip direction
measured in the field, the vertical depth you want to intersect below that point, and the hole dip.
It returns the collar position (UTM 47N + WGS84), hole azimuth, length to target, the angle at which
the hole cuts the structure, and the ground slope at the collar (from the 30 m DEM).

The hole is drilled from the hanging-wall side, i.e. azimuth = dip direction + 180, so it cuts the
structure at a high angle.

Examples
  # vein crops out at a grid point, dips 65 deg toward 120 deg, intersect 50 m below surface, hole -55
  python r1_collar_calc.py --e 779540 --n 2021560 --dipdir 120 --dip 65 --depth 50 --hole-dip 55
  # same, target given as lat/lon
  python r1_collar_calc.py --lat 18.2652 --lon 101.6436 --dipdir 120 --dip 65 --depth 50
"""

import argparse
import math

import numpy as np
import pyproj
import rasterio
from scipy.ndimage import label
from scipy.spatial import cKDTree

SITE = "drive-download-20261011T175941Z-1-001"
TO_UTM = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True)
TO_LL = pyproj.Transformer.from_crs("EPSG:32647", "EPSG:4326", always_xy=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--e", type=float, help="target surface easting (UTM 47N)")
    ap.add_argument("--n", type=float, help="target surface northing (UTM 47N)")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--dipdir", type=float, required=True, help="structure dip direction, deg from north (0-360)")
    ap.add_argument("--dip", type=float, required=True, help="structure dip, deg from horizontal (use 90 for vertical)")
    ap.add_argument("--depth", type=float, default=50, help="vertical depth of intersection below the target point (m)")
    ap.add_argument("--hole-dip", type=float, default=55, help="hole inclination below horizontal, deg (default 55)")
    ap.add_argument("--azimuth", type=float, default=None, help="override hole azimuth (default dipdir+180)")
    ap.add_argument("--overshoot", type=float, default=30, help="metres to drill past the intersection (default 30)")
    a = ap.parse_args()

    if a.e is None:
        if a.lat is None or a.lon is None:
            ap.error("give --e/--n or --lat/--lon")
        a.e, a.n = TO_UTM.transform(a.lon, a.lat)

    with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/07_Elevation.tif") as ds:
        dem, idx = ds.read(1).astype(float), ds.index
    with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/08_Slope.tif") as ds:
        slope = ds.read(1).astype(float)

    def z(e, n):
        r, c = idx(e, n)
        return float(dem[r, c])

    with rasterio.open(f"{SITE}/02_Maps/historical_cover_disagreement.tif") as ds:
        dis, tr = ds.read(1), ds.transform
    lbl, _ = label(dis == 1)
    ys, xs = np.where(lbl == 90)
    r1 = cKDTree(np.c_[tr.c + (xs + 0.5) * tr.a, tr.f + (ys + 0.5) * tr.e])

    al, dd, th = math.radians(a.dip), math.radians(a.dipdir), math.radians(a.hole_dip)
    az = math.radians(a.azimuth if a.azimuth is not None else (a.dipdir + 180) % 360)

    # intersection point: down-dip from the surface trace, a.depth below the target's elevation
    zt = z(a.e, a.n)
    h = 0.0 if a.dip >= 89.9 else a.depth / math.tan(al)
    P = np.array([a.e + h * math.sin(dd), a.n + h * math.cos(dd), zt - a.depth])
    u = np.array([math.cos(th) * math.sin(az), math.cos(th) * math.cos(az), -math.sin(th)])  # hole direction

    # back-project from P along -u until we reach the DEM surface
    L = a.depth / math.sin(th)
    for _ in range(50):
        C = P - L * u
        dz = z(C[0], C[1]) - C[2]
        if abs(dz) < 0.2:
            break
        L += dz / math.sin(th)
    C = P - L * u

    nrm = np.array([math.sin(al) * math.sin(dd), math.sin(al) * math.cos(dd), math.cos(al)])
    cut = math.degrees(math.asin(abs(float(u @ nrm))))
    lon, lat = TO_LL.transform(C[0], C[1])
    r, c = idx(C[0], C[1])

    print("R1 collar calculation (UTM 47N assumed - verify with GNSS)")
    print(f"  target surface point     E {a.e:.1f}  N {a.n:.1f}  elev {zt:.1f} m")
    print(f"  structure                dip {a.dip:.0f} deg toward {a.dipdir:.0f} deg")
    print(f"  intersection point       E {P[0]:.1f}  N {P[1]:.1f}  elev {P[2]:.1f} m ({a.depth:.0f} m below target)")
    print(f"  COLLAR                   E {C[0]:.1f}  N {C[1]:.1f}  elev {C[2]:.1f} m")
    print(f"                           lat {lat:.6f}  lon {lon:.6f}")
    print(f"  hole azimuth / dip       {math.degrees(az) % 360:.0f} deg / -{a.hole_dip:.0f} deg")
    print(f"  length to intersection   {L:.0f} m   planned total depth {L + a.overshoot:.0f} m")
    print(f"  hole cuts structure at   {cut:.0f} deg (aim >= 45; true width ~ {math.sin(math.radians(cut)):.2f} x core length)")
    print(f"  ground slope at collar   {slope[r, c]:.1f} deg (30 m DEM)   distance to R1 edge {r1.query(C[:2])[0]:.0f} m")
    if cut < 45:
        print("  WARNING: low intersection angle - steepen/flatten the hole or change azimuth")
    if slope[r, c] > 15:
        print("  WARNING: collar slope > 15 deg - check pad access on the ground or move along strike")


if __name__ == "__main__":
    main()
