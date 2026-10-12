#!/usr/bin/env python3
"""
Build the R1 on-site field pack: sampling grid, mapping traverses, drainage sampling points,
terrain-feasible drill-pad areas, and a map + GPX/KML/CSV for phones and GPS units.

Run with the `geo` conda env:  ~/miniconda3/envs/geo/bin/python make_r1_field_pack.py
Outputs go to outputs/r1_field/.
"""

import glob
import os
import re

import h5py
import matplotlib
import numpy as np
import pandas as pd
import pyproj
import rasterio
from scipy.ndimage import gaussian_filter, label
from scipy.spatial import cKDTree

matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

SITE = "drive-download-20261011T175941Z-1-001"
OUT = "outputs/r1_field"
os.makedirs(OUT, exist_ok=True)

TO_LL = pyproj.Transformer.from_crs("EPSG:32647", "EPSG:4326", always_xy=True)
TO_UTM = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True)

GRID_M = 40           # Phase A soil grid spacing
GRID_BUFFER_M = 40    # extend grid this far outside R1 cells
TRAVERSE_SPACING_M = 60
PAD_MAX_SLOPE = 15.0  # degrees, tracked/man-portable rig pad

# ------------------------------------------------------------------ R1 footprint (20 m cells)
with rasterio.open(f"{SITE}/02_Maps/historical_cover_disagreement.tif") as ds:
    dis, tr = ds.read(1), ds.transform
lbl, _ = label(dis == 1)
ys, xs = np.where(lbl == 90)
assert len(ys) == 98
r1_e = tr.c + (xs + 0.5) * tr.a
r1_n = tr.f + (ys + 0.5) * tr.e
r1_tree = cKDTree(np.c_[r1_e, r1_n])

# ------------------------------------------------------------------ DEM / slope (30 m)
with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/07_Elevation.tif") as ds:
    dem, dtr, dem_ds = ds.read(1).astype(float), ds.transform, ds
    dem_index = ds.index
with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/08_Slope.tif") as ds:
    slope = ds.read(1).astype(float)


def sample(arr, e, n):
    r, c = dem_index(e, n)
    return float(arr[r, c])


# ------------------------------------------------------------------ R1 long axis (ridge trend) from cell PCA
xy = np.c_[r1_e - r1_e.mean(), r1_n - r1_n.mean()]
evals, evecs = np.linalg.eigh(np.cov(xy.T))
long_axis = evecs[:, np.argmax(evals)]
long_az = (np.degrees(np.arctan2(long_axis[0], long_axis[1])) + 360) % 180  # azimuth 0-180
cross_az = (long_az + 90) % 180

# ------------------------------------------------------------------ zones (prior from satellite work; all are sampled)
CANDS = {
    "C10": (779502.0, 2021538.0), "C07": (779535.5, 2021584.5), "C06": (779435.5, 2021566.4),
    "C02": (779548.0, 2021496.0), "C01": (779467.5, 2021615.0), "C03": (779522.9, 2021664.3),
    "C04": (779588.6, 2021617.1), "C08": (779607.1, 2021464.3), "C05": (779330.0, 2021540.0),
    "C09": (779374.4, 2021583.3),
}


def zone(e, n):
    if n < 2021520 and e > 779480:
        return "S"   # south slope: most persistent EMIT Fe-oxide (C02, C08)
    if n > 2021630:
        return "N"   # summit flat (C03, C04)
    if e < 779420:
        return "W"   # western margin (C05, C09)
    return "C"       # central spur (C10, C07, C06, C01)


# ------------------------------------------------------------------ EMIT persistence per location (indicative only)
# dates where the R1 surface pattern was visible; 2026-01-21 and 2026-04-16 are not QC-clean (cloud edge / haze)
EMIT_DATES = ["20250122T064348", "20260121T063650", "20260125T050342", "20260416T070016"]
emit_layers = []
for k in EMIT_DATES:
    p = glob.glob(f"data/EMIT_L2B_MIN_*{k}*.nc")
    if not p:
        continue
    f = h5py.File(p[0], "r")
    lat, lon = f["location/lat"][:], f["location/lon"][:]
    md = f["mineral_metadata"]
    nm = {int(i): x.decode() for i, x in zip(md["index"][:], md["name"][:])}
    s = (lat > 18.260) & (lat < 18.272) & (lon > 101.637) & (lon < 101.650)
    rr, cc = np.where(s)
    e, n = TO_UTM.transform(lon[rr, cc], lat[rr, cc])
    g1 = f["group_1_mineral_id"][:][rr, cc]
    g2 = f["group_2_mineral_id"][:][rr, cc]
    fe = np.array([i > 0 and any(t in nm[i].lower() for t in ("goeth", "jaros", "hemat", "ferrihyd", "fe-hydrox")) for i in g1])
    ka = np.array([i > 0 and "kaol" in nm[i].lower() for i in g2])
    emit_layers.append((cKDTree(np.c_[e, n]), fe, ka))


def emit_counts(e, n):
    nfe = nka = 0
    for tree, fe, ka in emit_layers:
        d, j = tree.query([e, n])
        if d <= 45:
            nfe += int(fe[j])
            nka += int(ka[j])
    return nfe, nka


# ------------------------------------------------------------------ Phase A grid (40 m, aligned to ridge axis)
cx, cy = r1_e.mean(), r1_n.mean()
u = long_axis
v = np.array([-u[1], u[0]])
span = np.abs(xy @ np.c_[u, v]).max(axis=0) + GRID_BUFFER_M + GRID_M
pts = []
for a in np.arange(-span[0], span[0] + 1, GRID_M):
    for b in np.arange(-span[1], span[1] + 1, GRID_M):
        e, n = cx + a * u[0] + b * v[0], cy + a * u[1] + b * v[1]
        d = r1_tree.query([e, n])[0]
        if d <= GRID_BUFFER_M:
            pts.append((a, b, e, n, d))
pts.sort(key=lambda p: (-p[1], p[0]))
grid = []
for i, (a, b, e, n, d) in enumerate(pts, 1):
    lon_, lat_ = TO_LL.transform(e, n)
    nfe, nka = emit_counts(e, n)
    grid.append({
        "point_id": f"R1-G{i:03d}", "type": "soil_grid_40m", "zone": zone(e, n),
        "inside_R1": d <= 15, "easting": round(e, 1), "northing": round(n, 1),
        "lat": round(lat_, 6), "lon": round(lon_, 6),
        "elev_m": round(sample(dem, e, n), 1), "slope_deg": round(sample(slope, e, n), 1),
        "emit_fe_dates_of4": nfe, "emit_kaolin_dates_of4": nka,
    })
grid = pd.DataFrame(grid)

# ------------------------------------------------------------------ mapping traverses (perpendicular to ridge)
trav = []
half = span[1] + 20
for k, a in enumerate(np.arange(-span[0] + 20, span[0], TRAVERSE_SPACING_M), 1):
    p0 = (cx + a * u[0] - half * v[0], cy + a * u[1] - half * v[1])
    p1 = (cx + a * u[0] + half * v[0], cy + a * u[1] + half * v[1])
    trav.append({"line_id": f"R1-T{k:02d}", "e0": p0[0], "n0": p0[1], "e1": p1[0], "n1": p1[1]})
trav = pd.DataFrame(trav)

# ------------------------------------------------------------------ drainage: D8 flow from R1 downslope
r0, c0 = dem_index(cx - 1200, cy + 1200)
r1_, c1_ = dem_index(cx + 1200, cy - 1200)
W = gaussian_filter(dem[r0:r1_, c0:c1_], 0.7)
H, Wd = W.shape
nbr = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
recv = -np.ones((H, Wd, 2), int)
for r in range(1, H - 1):
    for c in range(1, Wd - 1):
        best, bb = 0.0, None
        for dr, dc in nbr:
            drop = (W[r, c] - W[r + dr, c + dc]) / (30 * np.hypot(dr, dc))
            if drop > best:
                best, bb = drop, (r + dr, c + dc)
        if bb:
            recv[r, c] = bb
acc = np.ones((H, Wd))
for idx in np.argsort(-W, axis=None):
    r, c = divmod(idx, Wd)
    if recv[r, c, 0] >= 0:
        acc[tuple(recv[r, c])] += acc[r, c]


def rc_to_en(r, c):
    return dtr.c + (c0 + c + 0.5) * dtr.a, dtr.f + (r0 + r + 0.5) * dtr.e


in_r1_dem = np.zeros((H, Wd), bool)
for r in range(H):
    for c in range(Wd):
        if r1_tree.query(rc_to_en(r, c))[0] <= 15:
            in_r1_dem[r, c] = True

flowlines = {}
for r, c in zip(*np.where(in_r1_dem)):
    path = []
    while recv[r, c, 0] >= 0 and len(path) < 200:
        r, c = recv[r, c]
        if not in_r1_dem[r, c]:
            path.append((r, c))
    if path:
        flowlines.setdefault(path[0], path)  # one line per exit cell

drain = []
seen = []
for k, path in enumerate(sorted(flowlines.values(), key=lambda p: -acc[p[min(len(p) - 1, 15)]]), 1):
    dist = 0.0
    prev = rc_to_en(*path[0])
    pending = [80, 250, 500, 800]
    for r, c in path:
        e, n = rc_to_en(r, c)
        dist += np.hypot(e - prev[0], n - prev[1])
        prev = (e, n)
        hit = [t for t in pending if dist >= t]
        for target in hit[:1]:
            pending = [t for t in pending if t > dist]
            if all(np.hypot(e - s[0], n - s[1]) > 70 for s in seen):
                seen.append((e, n))
                lon_, lat_ = TO_LL.transform(e, n)
                drain.append({"point_id": f"R1-D{len(drain) + 1:02d}", "type": "stream_sediment_pan",
                              "dist_from_R1_m": target, "upstream_cells": int(acc[r, c]),
                              "easting": round(e, 1), "northing": round(n, 1), "lat": round(lat_, 6),
                              "lon": round(lon_, 6), "elev_m": round(sample(dem, e, n), 1)})
drain = pd.DataFrame(drain)
drain = drain[drain.upstream_cells >= 3].reset_index(drop=True)
drain["point_id"] = [f"R1-D{i + 1:02d}" for i in range(len(drain))]

# ------------------------------------------------------------------ terrain-feasible pad areas (logistics only)
pads = []
rr0, cc0 = dem_index(cx - 300, cy + 300)
rr1, cc1 = dem_index(cx + 300, cy - 300)
for r in range(rr0, rr1):
    for c in range(cc0, cc1):
        e, n = dtr.c + (c + 0.5) * dtr.a, dtr.f + (r + 0.5) * dtr.e
        if slope[r, c] <= PAD_MAX_SLOPE and r1_tree.query([e, n])[0] <= 80:
            lon_, lat_ = TO_LL.transform(e, n)
            pads.append({"easting": round(e, 1), "northing": round(n, 1), "lat": round(lat_, 6), "lon": round(lon_, 6),
                         "slope_deg": round(float(slope[r, c]), 1), "elev_m": round(float(dem[r, c]), 1), "zone": zone(e, n)})
pads = pd.DataFrame(pads)

# ------------------------------------------------------------------ write CSV / GPX / KML
grid.to_csv(f"{OUT}/r1_soil_grid_40m.csv", index=False)
drain.to_csv(f"{OUT}/r1_drainage_points.csv", index=False)
pads.to_csv(f"{OUT}/r1_pad_feasible_cells.csv", index=False)
tl = trav.copy()
tl["lon0"], tl["lat0"] = TO_LL.transform(tl.e0.values, tl.n0.values)
tl["lon1"], tl["lat1"] = TO_LL.transform(tl.e1.values, tl.n1.values)
tl.round(6).to_csv(f"{OUT}/r1_traverses.csv", index=False)

ref = pd.DataFrame([{"point_id": k, "easting": v[0], "northing": v[1]} for k, v in CANDS.items()])
ref["lon"], ref["lat"] = TO_LL.transform(ref.easting.values, ref.northing.values)

outline_ll = [TO_LL.transform(e, n) for e, n in zip(r1_e, r1_n)]

gpx = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<gpx version="1.1" creator="make_r1_field_pack.py" xmlns="http://www.topografix.com/GPX/1/1">']
for _, p in grid.iterrows():
    gpx.append(f'<wpt lat="{p.lat}" lon="{p.lon}"><ele>{p.elev_m}</ele><name>{p.point_id}</name>'
               f'<desc>zone {p.zone}; soil grid 40 m</desc><sym>Flag, Blue</sym></wpt>')
for _, p in drain.iterrows():
    gpx.append(f'<wpt lat="{p.lat}" lon="{p.lon}"><ele>{p.elev_m}</ele><name>{p.point_id}</name>'
               f'<desc>stream sediment / panning, ~{p.dist_from_R1_m} m below R1</desc><sym>Flag, Green</sym></wpt>')
for _, p in ref.iterrows():
    gpx.append(f'<wpt lat="{p.lat:.6f}" lon="{p.lon:.6f}"><name>old-{p.point_id}</name>'
               f'<desc>reference only, from earlier satellite plan</desc><sym>Pin, Red</sym></wpt>')
for _, t in tl.iterrows():
    gpx.append(f'<trk><name>{t.line_id}</name><trkseg><trkpt lat="{t.lat0:.6f}" lon="{t.lon0:.6f}"/>'
               f'<trkpt lat="{t.lat1:.6f}" lon="{t.lon1:.6f}"/></trkseg></trk>')
gpx.append("</gpx>")
open(f"{OUT}/r1_field_pack.gpx", "w").write("\n".join(gpx))

kml = ['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
       '<name>R1 field pack</name>',
       '<Style id="g"><IconStyle><color>ffff8800</color><scale>0.6</scale></IconStyle></Style>',
       '<Style id="d"><IconStyle><color>ff00cc00</color><scale>0.8</scale></IconStyle></Style>',
       '<Style id="r"><IconStyle><color>ff8080ff</color><scale>0.5</scale></IconStyle></Style>',
       '<Style id="t"><LineStyle><color>ff00ffff</color><width>2</width></LineStyle></Style>',
       '<Style id="o"><IconStyle><color>ff0099ff</color><scale>0.3</scale></IconStyle></Style>']
kml.append("<Folder><name>R1 cells (20 m)</name>")
for lo, la in outline_ll:
    kml.append(f'<Placemark><styleUrl>#o</styleUrl><Point><coordinates>{lo:.6f},{la:.6f}</coordinates></Point></Placemark>')
kml.append("</Folder><Folder><name>Soil grid 40 m</name>")
for _, p in grid.iterrows():
    kml.append(f'<Placemark><name>{p.point_id}</name><description>zone {p.zone}, elev {p.elev_m} m, slope {p.slope_deg} deg'
               f'</description><styleUrl>#g</styleUrl><Point><coordinates>{p.lon},{p.lat}</coordinates></Point></Placemark>')
kml.append("</Folder><Folder><name>Drainage / panning</name>")
for _, p in drain.iterrows():
    kml.append(f'<Placemark><name>{p.point_id}</name><description>~{p.dist_from_R1_m} m below R1</description>'
               f'<styleUrl>#d</styleUrl><Point><coordinates>{p.lon},{p.lat}</coordinates></Point></Placemark>')
kml.append("</Folder><Folder><name>Mapping traverses</name>")
for _, t in tl.iterrows():
    kml.append(f'<Placemark><name>{t.line_id}</name><styleUrl>#t</styleUrl><LineString><coordinates>'
               f'{t.lon0:.6f},{t.lat0:.6f} {t.lon1:.6f},{t.lat1:.6f}</coordinates></LineString></Placemark>')
kml.append("</Folder><Folder><name>Old C01-C10 (reference only)</name>")
for _, p in ref.iterrows():
    kml.append(f'<Placemark><name>old-{p.point_id}</name><styleUrl>#r</styleUrl>'
               f'<Point><coordinates>{p.lon:.6f},{p.lat:.6f}</coordinates></Point></Placemark>')
kml.append("</Folder></Document></kml>")
open(f"{OUT}/r1_field_pack.kml", "w").write("\n".join(kml))

# ------------------------------------------------------------------ map
fig, ax = plt.subplots(figsize=(11, 10))
x0, x1, y0, y1 = cx - 450, cx + 450, cy - 420, cy + 380
ra, ca = dem_index(x0, y1)
rb, cb = dem_index(x1, y0)
sub = gaussian_filter(dem[ra:rb + 1, ca:cb + 1], 0.8)
ext = [dtr.c + ca * dtr.a, dtr.c + (cb + 1) * dtr.a, dtr.f + (rb + 1) * dtr.e, dtr.f + ra * dtr.e]
gy, gx = np.gradient(sub, 30, 30)
hs = np.clip(np.sin(np.radians(45)) * np.cos(np.arctan(np.hypot(gx, gy)))
             + np.cos(np.radians(45)) * np.sin(np.arctan(np.hypot(gx, gy))) * np.cos(np.radians(315) - np.arctan2(-gx, gy)), 0, 1)
ax.imshow(hs, extent=ext, cmap="gray", alpha=0.55)
cs = ax.contour(np.linspace(ext[0], ext[1], sub.shape[1]), np.linspace(ext[3], ext[2], sub.shape[0]), sub,
                levels=np.arange(300, 460, 10), colors="#7a5c3a", linewidths=0.6)
ax.clabel(cs, fontsize=7, fmt="%d")
if len(pads):
    ax.scatter(pads.easting, pads.northing, marker="s", s=150, color="#9be39b", alpha=0.45, lw=0,
               label=f"Slope <= {PAD_MAX_SLOPE:.0f} deg (pad-feasible, 30 m DEM)")
for e, n in zip(r1_e, r1_n):
    ax.add_patch(plt.Rectangle((e - 10, n - 10), 20, 20, fc="#f59e0b", ec="none", alpha=0.35))
for _, t in trav.iterrows():
    ax.plot([t.e0, t.e1], [t.n0, t.n1], color="#0891b2", lw=1.2, ls="--")
    ax.text(t.e1, t.n1, t.line_id, fontsize=7, color="#0e7490")
for path in flowlines.values():
    en = np.array([rc_to_en(r, c) for r, c in path])
    ax.plot(en[:, 0], en[:, 1], color="#2563eb", lw=0.8, alpha=0.6)
zc = {"S": "#dc2626", "C": "#9333ea", "N": "#0d9488", "W": "#ca8a04"}
for z, g in grid.groupby("zone"):
    ax.scatter(g.easting, g.northing, s=22, color=zc[z], edgecolor="white", lw=0.6, zorder=5, label=f"Soil grid, zone {z}")
for _, p in grid.iterrows():
    ax.text(p.easting + 4, p.northing + 4, p.point_id[-3:], fontsize=5.5, color="#333", zorder=6)
if len(drain):
    ax.scatter(drain.easting, drain.northing, marker="v", s=70, color="#16a34a", edgecolor="black", zorder=6,
               label="Stream sediment / panning")
    for _, p in drain.iterrows():
        ax.text(p.easting + 6, p.northing - 12, p.point_id, fontsize=7, color="#166534", weight="bold",
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])
ax.scatter(ref.easting, ref.northing, marker="x", s=30, color="#555", zorder=4, label="Old C01-C10 (reference only)")
ax.set_xlim(x0, x1)
ax.set_ylim(y0, y1)
ax.set_aspect("equal")
ax.set_title("R1 field pack: 40 m soil grid, traverses, drainage sampling, pad-feasible ground\n"
             f"UTM 47N (unverified CRS) | ridge axis ~{long_az:.0f} deg, traverses ~{cross_az:.0f} deg", fontsize=11)
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")
ax.grid(alpha=0.3)
ax.legend(loc="lower left", fontsize=7.5, framealpha=0.9)
ax.annotate("N", xy=(x1 - 40, y1 - 40), xytext=(x1 - 40, y1 - 110), ha="center", fontsize=12, weight="bold",
            arrowprops=dict(arrowstyle="-|>", color="black"))
plt.tight_layout()
fig.savefig(f"{OUT}/r1_field_map.png", dpi=200)

print(f"ridge long axis azimuth ~{long_az:.0f} deg; traverse azimuth ~{cross_az:.0f} deg")
print(f"grid points: {len(grid)} (inside R1: {int(grid.inside_R1.sum())}); by zone: {grid.zone.value_counts().to_dict()}")
print(f"traverses: {len(trav)}; drainage points: {len(drain)}; pad-feasible 30 m cells: {len(pads)} "
      f"by zone {pads.zone.value_counts().to_dict() if len(pads) else {}}")
print(drain.to_string(index=False))
print(grid.groupby("zone")[["elev_m", "slope_deg", "emit_fe_dates_of4", "emit_kaolin_dates_of4"]].mean().round(1))
print(f"wrote {sorted(os.listdir(OUT))}")
