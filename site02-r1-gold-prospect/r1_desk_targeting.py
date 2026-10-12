#!/usr/bin/env python3
"""
Desk-only drill-candidate ranking inside R1 (no field data).

Evidence layers, all resampled to the 98 R1 cells (20 m):
  1. Sentinel-2 (10/20 m), bare-period Dec 2024 - May 2025: ferric-iron ratio (B4/B2), 0.9 um Fe3+ depth,
     SWIR clay ratio (B11/B12) - computed on bare observations only and ranked against other bare ground
     within 1.5 km of R1
  2. Sentinel-2 bare frequency (how often the cell was actually exposed) - reliability of (1)
  3. EMIT L2B MIN persistence (Fe-oxide and kaolin detections, 4 dates)
  4. Structure proxy: straight drainage segments on the 30 m DEM (drainage often follows fractures);
     dominant trends from a rose of segments over the Site 02 DEM; distance from each cell to the nearest
     segment parallel to a dominant trend
  5. Geomorphic position: height above nearest drainage (HAND) - higher = less chance of transported cover
  6. Logistics: slope and pad feasibility (gate, not score)

Outputs: outputs/r1_desk/ (cell table, candidate table, maps).
Run with: ~/miniconda3/envs/geo/bin/python r1_desk_targeting.py
"""

import glob
import math
import os

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
from matplotlib.colors import ListedColormap

SITE = "drive-download-20261011T175941Z-1-001"
OUT = "outputs/r1_desk"
os.makedirs(OUT, exist_ok=True)
TO_LL = pyproj.Transformer.from_crs("EPSG:32647", "EPSG:4326", always_xy=True)
TO_UTM = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True)

# ------------------------------------------------------------------ R1 cells
with rasterio.open(f"{SITE}/02_Maps/historical_cover_disagreement.tif") as ds:
    dis, tr = ds.read(1), ds.transform
lbl, _ = label(dis == 1)
ys, xs = np.where(lbl == 90)
cells = pd.DataFrame({"e": tr.c + (xs + 0.5) * tr.a, "n": tr.f + (ys + 0.5) * tr.e})
r1_tree = cKDTree(cells[["e", "n"]].values)

# ------------------------------------------------------------------ 1-2. Sentinel-2 stack
P1 = ("2024-11-01", "2025-05-31")   # bare period at R1
P2 = ("2025-10-01", "2026-10-31")   # revegetated period
stack = {"P1": [], "P2": []}
bounds = None
for f in sorted(glob.glob("data/s2_r1/*.npz")):
    z = np.load(f)
    d = str(z["date"])
    per = "P1" if P1[0] <= d <= P1[1] else "P2" if P2[0] <= d <= P2[1] else None
    if per is None:
        continue
    bounds = z["bounds"]
    scl = z["SCL"]
    clear = np.isin(scl, [4, 5])
    b = {k: z[k] for k in ["B02", "B03", "B04", "B05", "B08", "B8A", "B11", "B12"]}
    ndvi = (b["B08"] - b["B04"]) / (b["B08"] + b["B04"] + 1e-6)
    cont = b["B05"] + (b["B11"] - b["B05"]) * (865 - 705) / (1610 - 705)
    stack[per].append({
        "date": d, "clear": clear, "ndvi": ndvi,
        "feox": b["B04"] / np.maximum(b["B02"], 0.005),
        "fe900": 1 - b["B8A"] / np.maximum(cont, 0.005),
        "clay": b["B11"] / np.maximum(b["B12"], 0.005),
        "rgb": np.dstack([b["B04"], b["B03"], b["B02"]]),
    })
print({k: len(v) for k, v in stack.items()}, "Sentinel-2 scenes per period")
x0, y0, x1, y1 = bounds
H = stack["P1"][0]["ndvi"].shape[0]
S2RES = (x1 - x0) / H


def period_layers(per):
    L = stack[per]
    clear = np.stack([s["clear"] for s in L])
    ndvi = np.where(clear, np.stack([s["ndvi"] for s in L]), np.nan)
    bare = clear & (ndvi < 0.30)
    out = {"n_clear": clear.sum(0), "bare_freq": bare.sum(0) / np.maximum(clear.sum(0), 1),
           "ndvi_med": np.nanmedian(ndvi, 0)}
    for k in ("feox", "fe900", "clay"):
        v = np.where(bare, np.stack([s[k] for s in L]), np.nan)
        out[k] = np.nanmedian(v, 0)
    rgb = np.stack([s["rgb"] for s in L])
    rgb = np.where(clear[..., None], rgb, np.nan)
    out["rgb"] = np.nanmedian(rgb, 0)
    return out


import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
S = {p: period_layers(p) for p in ("P1", "P2")}


def s2_at(arr, e, n, k=1):
    c = int((e - x0) / S2RES)
    r = int((y1 - n) / S2RES)
    return float(np.nanmean(arr[r - k + 1:r + k, c - k + 1:c + k]))   # 2x2 10 m px ~ one 20 m cell


for key in ("bare_freq", "ndvi_med", "feox", "fe900", "clay"):
    cells[f"s2p1_{key}"] = [s2_at(S["P1"][key], e, n) for e, n in zip(cells.e, cells.n)]
cells["s2p2_bare_freq"] = [s2_at(S["P2"]["bare_freq"], e, n) for e, n in zip(cells.e, cells.n)]

# local bare-ground reference: P1 pixels in the window, bare >= 50% of clear dates, outside R1
yy, xx = np.mgrid[0:H, 0:H]
pe_ = x0 + (xx + 0.5) * S2RES
pn_ = y1 - (yy + 0.5) * S2RES
outside = r1_tree.query(np.c_[pe_.ravel(), pn_.ravel()])[0].reshape(H, H) > 30
ref_mask = outside & (S["P1"]["bare_freq"] >= 0.5) & (S["P1"]["n_clear"] >= 5)
print("reference bare pixels (10 m) outside R1:", int(ref_mask.sum()))
for key in ("feox", "fe900", "clay"):
    ref = S["P1"][key][ref_mask]
    ref = ref[np.isfinite(ref)]
    cells[f"pct_{key}"] = [float((ref < v).mean() * 100) if np.isfinite(v) else np.nan for v in cells[f"s2p1_{key}"]]
    cells[f"ref_{key}_p50"] = np.median(ref)

# ------------------------------------------------------------------ 3. EMIT persistence per cell
EMIT_DATES = ["20250122T064348", "20260121T063650", "20260125T050342", "20260416T070016"]
cells["emit_fe"] = 0
cells["emit_kaol"] = 0
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
    g1, g2 = f["group_1_mineral_id"][:][rr, cc], f["group_2_mineral_id"][:][rr, cc]
    fe = np.array([i > 0 and any(t in nm[i].lower() for t in ("goeth", "jaros", "hemat", "ferrihyd", "fe-hydrox")) for i in g1])
    ka = np.array([i > 0 and "kaol" in nm[i].lower() for i in g2])
    d, j = cKDTree(np.c_[e, n]).query(cells[["e", "n"]].values)
    ok = d <= 45
    cells.loc[ok, "emit_fe"] += fe[j[ok]].astype(int)
    cells.loc[ok, "emit_kaol"] += ka[j[ok]].astype(int)

# ------------------------------------------------------------------ 4-5. DEM: drainage, structure proxy, HAND, slope
with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/07_Elevation.tif") as ds:
    dem, dtr, dem_index = ds.read(1).astype(float), ds.transform, ds.index
with rasterio.open(f"{SITE}/02_Maps/Map_Sheets/08_Slope.tif") as ds:
    slope = ds.read(1).astype(float)
Z = gaussian_filter(np.where(np.isfinite(dem), dem, np.nanmean(dem)), 0.7)
R, C = Z.shape
nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
rcv = -np.ones((R, C), int)
for r in range(1, R - 1):
    for c in range(1, C - 1):
        best, bi = 0.0, -1
        for k, (dr, dc) in enumerate(nb):
            g = (Z[r, c] - Z[r + dr, c + dc]) / math.hypot(dr, dc)
            if g > best:
                best, bi = g, (r + dr) * C + (c + dc)
        rcv[r, c] = bi
acc = np.ones(R * C)
for i in np.argsort(-Z, axis=None):
    j = rcv.flat[i]
    if j >= 0:
        acc[j] += acc[i]
acc = acc.reshape(R, C)
stream = acc >= 25                                   # ~2.3 ha catchment

# HAND: elevation above the stream cell reached by following flow
hand = np.full((R, C), np.nan)
for r in range(R):
    for c in range(C):
        i, steps = r * C + c, 0
        while not stream.flat[i] and rcv.flat[i] >= 0 and steps < 300:
            i, steps = rcv.flat[i], steps + 1
        hand[r, c] = Z[r, c] - Z.flat[i]


def rc_en(r, c):
    return dtr.c + (c + 0.5) * dtr.a, dtr.f + (r + 0.5) * dtr.e


# straight drainage segments: walk each stream path in 8-cell chunks, keep near-straight chunks
segs = []
heads = [(r, c) for r in range(R) for c in range(C) if stream[r, c]]
visited = set()
for r, c in heads:
    i = r * C + c
    path = []
    while i >= 0 and stream.flat[i] and i not in visited:
        visited.add(i)
        path.append(divmod(i, C))
        i = rcv.flat[i]
    for k in range(0, len(path) - 8, 4):
        pts = np.array([rc_en(*p) for p in path[k:k + 9]])
        v = pts[-1] - pts[0]
        length = np.hypot(*v)
        sinuosity = np.sum(np.hypot(*np.diff(pts, axis=0).T)) / max(length, 1)
        if length >= 200 and sinuosity < 1.15:
            segs.append((pts[0][0], pts[0][1], pts[-1][0], pts[-1][1],
                         (math.degrees(math.atan2(v[0], v[1])) + 360) % 180, length))
segs = pd.DataFrame(segs, columns=["e0", "n0", "e1", "n1", "az", "len"])
hist, edges = np.histogram(segs.az, bins=18, range=(0, 180), weights=segs.len)
order = np.argsort(-hist)
trends = []
for b in order:
    centre = edges[b] + 5
    if all(min(abs(centre - t), 180 - abs(centre - t)) > 40 for t in trends):
        trends.append(centre)
    if len(trends) == 2:
        break
print("straight drainage segments:", len(segs), "dominant trends (deg):", trends)

segs["trend_match"] = segs.az.apply(lambda a: min(min(abs(a - t), 180 - abs(a - t)) for t in trends) <= 15)
lin = segs[segs.trend_match]


def dist_to_segments(e, n, S_):
    best = 1e9
    for s in S_.itertuples():
        p0, p1 = np.array([s.e0, s.n0]), np.array([s.e1, s.n1])
        v = p1 - p0
        t = np.clip(np.dot([e, n] - p0, v) / np.dot(v, v), 0, 1)
        best = min(best, np.hypot(*([e, n] - (p0 + t * v))))
    return best


# extend each trend-parallel segment 300 m both ways (a fracture continues beyond the straight valley)
ext = lin.copy()
for i_, s in lin.iterrows():
    v = np.array([s.e1 - s.e0, s.n1 - s.n0])
    v /= np.linalg.norm(v)
    ext.loc[i_, ["e0", "n0"]] = [s.e0 - 300 * v[0], s.n0 - 300 * v[1]]
    ext.loc[i_, ["e1", "n1"]] = [s.e1 + 300 * v[0], s.n1 + 300 * v[1]]
near = ext[[dist_to_segments(cells.e.mean(), cells.n.mean(), ext.loc[[i]]) < 600 for i in ext.index]]
cells["dist_lineament_m"] = [dist_to_segments(e, n, near) if len(near) else np.nan for e, n in zip(cells.e, cells.n)]
cells["hand_m"] = [hand[dem_index(e, n)] for e, n in zip(cells.e, cells.n)]
cells["elev_m"] = [dem[dem_index(e, n)] for e, n in zip(cells.e, cells.n)]
cells["slope_deg"] = [slope[dem_index(e, n)] for e, n in zip(cells.e, cells.n)]

# ------------------------------------------------------------------ 6. scoring (desk-only, transparent)
def rank01(s):
    return s.rank(pct=True).fillna(0)


cells["sc_spectral_s2"] = (rank01(cells.pct_clay) + rank01(cells.pct_feox) + rank01(cells.pct_fe900)) / 3
cells["sc_emit"] = (cells.emit_fe + cells.emit_kaol) / 8
cells["sc_exposure"] = cells.s2p1_bare_freq.clip(0, 1)
cells["sc_structure"] = np.exp(-cells.dist_lineament_m / 60).fillna(0)
cells["sc_insitu"] = rank01(cells.hand_m)
# no DEM lineament crosses R1 (nearest is >130 m away), so structure gets a low weight
W = {"sc_spectral_s2": 0.35, "sc_emit": 0.15, "sc_exposure": 0.20, "sc_structure": 0.10, "sc_insitu": 0.20}
cells["score"] = sum(cells[k] * w for k, w in W.items())
cells["lon"], cells["lat"] = TO_LL.transform(cells.e.values, cells.n.values)

# smooth the score over a 30 m neighbourhood (a drill target is not a single 20 m cell)
xy_ = cells[["e", "n"]].values
nbrs = r1_tree.query_ball_point(xy_, 30)
cells["score_s"] = [cells.score.iloc[i].mean() for i in nbrs]

MIN_SEP, N_CAND = 70, 4


def pick(score_col):
    order = cells.sort_values(score_col, ascending=False)
    chosen = []
    for i, r in order.iterrows():
        if all(np.hypot(r.e - cells.e[j], r.n - cells.n[j]) >= MIN_SEP for j in chosen):
            chosen.append(i)
        if len(chosen) == N_CAND:
            break
    return chosen


peaks = pick("score_s")

# sensitivity: re-pick under alternative weightings; count how often each peak's area (<= 40 m) is re-selected
ALT = {
    "equal": {k: 0.2 for k in W},
    "spectral_only": {"sc_spectral_s2": 1.0},
    "no_emit": {"sc_spectral_s2": 0.45, "sc_exposure": 0.20, "sc_structure": 0.10, "sc_insitu": 0.25},
    "insitu_heavy": {"sc_spectral_s2": 0.30, "sc_emit": 0.10, "sc_exposure": 0.15, "sc_structure": 0.05, "sc_insitu": 0.40},
    "emit_heavy": {"sc_spectral_s2": 0.25, "sc_emit": 0.40, "sc_exposure": 0.15, "sc_structure": 0.05, "sc_insitu": 0.15},
}
alt_picks = {}
for name, w in ALT.items():
    cells[f"alt_{name}"] = sum(cells[k] * v for k, v in w.items())
    cells[f"alt_{name}"] = [cells[f"alt_{name}"].iloc[i].mean() for i in nbrs]
    alt_picks[name] = pick(f"alt_{name}")

cands = []
for i in peaks:
    g = cells.iloc[r1_tree.query_ball_point(xy_[i], 30)]
    w_ = g.score
    e, n = np.average(g.e, weights=w_), np.average(g.n, weights=w_)
    cands.append({"cells": len(g), "area_m2": 400 * len(g), "score_mean": g.score.mean(), "score_max": g.score.max(),
                  "e": e, "n": n, "elev_m": dem[dem_index(e, n)], "slope_deg": slope[dem_index(e, n)],
                  "s2_clay_pct": g.pct_clay.mean(), "s2_feox_pct": g.pct_feox.mean(), "s2_fe900_pct": g.pct_fe900.mean(),
                  "bare_freq_p1": g.s2p1_bare_freq.mean(), "emit_fe_of4": g.emit_fe.mean(), "emit_kaol_of4": g.emit_kaol.mean(),
                  "dist_lineament_m": g.dist_lineament_m.mean(), "hand_m": g.hand_m.mean(),
                  "robust_in_alt_weightings": sum(any(np.hypot(cells.e[i] - cells.e[j], cells.n[i] - cells.n[j]) <= 40
                                                      for j in p) for p in alt_picks.values()),
                  "members": g.index.tolist()})
cands = pd.DataFrame(cands).reset_index(drop=True)
cands.insert(0, "candidate", [f"DT-{i + 1}" for i in range(len(cands))])
cands["lon"], cands["lat"] = TO_LL.transform(cands.e.values, cands.n.values)


# provisional hole: vertical structure along the nearest dominant trend; drill perpendicular, -60, 50 m
def nearest_trend_az(e, n):
    if not len(near):
        return trends[0]
    dd = [dist_to_segments(e, n, near.loc[[i]]) for i in near.index]
    return float(near.loc[near.index[int(np.argmin(dd))], "az"])


TARGET_DEPTH = 50  # m below the target's ground surface
holes = []
for c in cands.itertuples():
    strike = nearest_trend_az(c.e, c.n)
    zt = dem[dem_index(c.e, c.n)] - TARGET_DEPTH
    best = None
    # search collar positions 15-110 m from the target; hole aims straight at the target point at depth
    for r_ in range(15, 111, 5):
        for a_ in range(0, 360, 5):
            ce = c.e + r_ * math.sin(math.radians(a_))
            cn = c.n + r_ * math.cos(math.radians(a_))
            zc = dem[dem_index(ce, cn)]
            dip = math.degrees(math.atan2(zc - zt, r_))
            if not 45 <= dip <= 65:
                continue
            az = (a_ + 180) % 360
            # angle between the hole and a vertical plane striking along the assumed trend
            cut_deg = math.degrees(math.asin(abs(math.sin(math.radians(az - strike))) * math.cos(math.radians(dip))))
            sl = slope[dem_index(ce, cn)]
            # rank: cut the assumed structure at >= 35 deg first, then pad slope <= 15 deg, then shortest hole
            key = (cut_deg < 35, sl > 15, math.hypot(r_, zc - zt))
            if best is None or key < best[0]:
                best = (key, ce, cn, zc, az, dip, cut_deg, sl, math.hypot(r_, zc - zt))
    _, ce, cn, zc, az, dip, cut_deg, sl, L = best
    lo, la = TO_LL.transform(ce, cn)
    holes.append({"candidate": c.candidate, "assumed_strike": round(strike), "hole_azimuth": round(az), "hole_dip": -round(dip),
                  "collar_e": round(ce, 1), "collar_n": round(cn, 1), "collar_lat": round(la, 6), "collar_lon": round(lo, 6),
                  "collar_elev": round(zc, 1), "collar_slope": round(sl, 1), "cut_angle_vs_assumed_structure": round(cut_deg),
                  "length_to_target_m": round(L), "planned_depth_m": int(math.ceil((L + 40) / 10) * 10)})
holes = pd.DataFrame(holes)

cells.round(4).to_csv(f"{OUT}/r1_cells_evidence.csv", index_label="cell")
cands.drop(columns="members").round(3).to_csv(f"{OUT}/r1_desk_candidates.csv", index=False)
holes.to_csv(f"{OUT}/r1_desk_provisional_holes.csv", index=False)
segs.round(1).to_csv(f"{OUT}/dem_straight_drainage_segments.csv", index=False)

# ------------------------------------------------------------------ maps
ext_s2 = [x0, x1, y0, y1]
pad = 260
cx, cy = cells.e.mean(), cells.n.mean()
view = (cx - pad - 80, cx + pad + 80, cy - pad, cy + pad)


def stretch(a, lo=2, hi=98):
    v = a[np.isfinite(a)]
    p0, p1 = np.percentile(v, [lo, hi])
    return np.clip((a - p0) / (p1 - p0), 0, 1)


def truecolor(rgb):
    # fixed reflectance range + gamma so bright bare soil keeps its colour next to dark forest
    return np.clip(np.nan_to_num(rgb) / 0.30, 0, 1) ** 0.6


def r1_outline(ax, **kw):
    for e, n in zip(cells.e, cells.n):
        ax.add_patch(plt.Rectangle((e - 10, n - 10), 20, 20, fill=False, **kw))


fig, axs = plt.subplots(2, 3, figsize=(18, 12))
panels = [
    ("Sentinel-2 true colour, bare period (median Dec 2024 - May 2025)", "rgbP1"),
    ("Sentinel-2 true colour, recent (median Oct 2025 - Oct 2026)", "rgbP2"),
    ("Bare frequency Dec 2024 - May 2025 (share of clear dates NDVI < 0.3)", "bare"),
    ("SWIR clay ratio B11/B12 (bare obs only)", "clay"),
    ("Ferric iron ratio B4/B2 (bare obs only)", "feox"),
    ("Desk score per R1 cell + straight drainage (structure proxy)", "score"),
]
for ax, (title, key) in zip(axs.ravel(), panels):
    if key.startswith("rgb"):
        rgb = S["P1" if key == "rgbP1" else "P2"]["rgb"]
        ax.imshow(truecolor(rgb), extent=ext_s2)
    elif key == "bare":
        im = ax.imshow(S["P1"]["bare_freq"], extent=ext_s2, cmap="YlOrBr", vmin=0, vmax=1)
        plt.colorbar(im, ax=ax, fraction=0.04)
    elif key in ("clay", "feox"):
        a = np.where(S["P1"]["bare_freq"] >= 0.3, S["P1"][key], np.nan)
        im = ax.imshow(a, extent=ext_s2, cmap="viridis" if key == "clay" else "inferno",
                       vmin=np.nanpercentile(a, 5), vmax=np.nanpercentile(a, 95))
        plt.colorbar(im, ax=ax, fraction=0.04)
    else:
        ax.imshow(truecolor(S["P1"]["rgb"]), extent=ext_s2, alpha=0.55)
        sc = ax.scatter(cells.e, cells.n, c=cells.score, cmap="RdYlBu_r", s=95, marker="s", edgecolor="none")
        plt.colorbar(sc, ax=ax, fraction=0.04)
        for s in segs.itertuples():
            ax.plot([s.e0, s.e1], [s.n0, s.n1], color="#1d4ed8" if s.trend_match else "#93c5fd",
                    lw=2.2 if s.trend_match else 1)
    if key != "score":
        r1_outline(ax, ec="white", lw=0.4, alpha=0.8)
    for c in cands.itertuples():
        ax.scatter(c.e, c.n, marker="*", s=260, color="#ef4444", edgecolor="white", lw=1.2, zorder=10)
        ax.text(c.e + 12, c.n + 10, c.candidate, color="white", fontsize=10, weight="bold", zorder=11,
                path_effects=[pe.withStroke(linewidth=3, foreground="black")])
    ax.set_xlim(view[0], view[1])
    ax.set_ylim(view[2], view[3])
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=7)
fig.suptitle("R1 desk-only evidence (Sentinel-2 10/20 m, EMIT, DEM) - UTM 47N, unverified CRS", fontsize=13)
plt.tight_layout()
fig.savefig(f"{OUT}/r1_desk_evidence_panels.png", dpi=150)
plt.close(fig)

# single candidate map (field-pack style)
fig, ax = plt.subplots(figsize=(11, 10))
ax.imshow(truecolor(S["P1"]["rgb"]), extent=ext_s2)
r0_, c0_ = dem_index(view[0] - 100, view[3] + 100)
r1x, c1x = dem_index(view[1] + 100, view[2] - 100)
sub = gaussian_filter(dem[r0_:r1x + 1, c0_:c1x + 1], 0.8)
xs_ = dtr.c + (np.arange(c0_, c1x + 1) + 0.5) * dtr.a
ys_ = dtr.f + (np.arange(r0_, r1x + 1) + 0.5) * dtr.e
cs = ax.contour(xs_, ys_, sub, levels=np.arange(300, 470, 10), colors="#fde68a", linewidths=0.6, alpha=0.8)
ax.clabel(cs, fontsize=7, fmt="%d")
r1_outline(ax, ec="#f59e0b", lw=0.6)
for s in segs.itertuples():
    if s.trend_match:
        ax.plot([s.e0, s.e1], [s.n0, s.n1], color="#38bdf8", lw=2.5, alpha=0.9)
for _, c in cands.iterrows():
    mem = cells.loc[c.members]
    ax.scatter(mem.e, mem.n, marker="s", s=120, facecolor="none", edgecolor="#ef4444", lw=1.4)
for c, h in zip(cands.itertuples(), holes.itertuples()):
    ax.annotate("", xy=(c.e, c.n), xytext=(h.collar_e, h.collar_n),
                arrowprops=dict(arrowstyle="-|>", color="#22c55e", lw=2.2))
    ax.scatter(h.collar_e, h.collar_n, marker="o", s=60, color="#22c55e", edgecolor="black", zorder=9)
    ax.scatter(c.e, c.n, marker="*", s=380, color="#ef4444", edgecolor="white", lw=1.4, zorder=10)
    ax.text(c.e + 14, c.n + 12, f"{c.candidate}", color="white", fontsize=12, weight="bold", zorder=11,
            path_effects=[pe.withStroke(linewidth=3, foreground="black")])
ax.plot([], [], color="#38bdf8", lw=2.5, label=f"Straight drainage on dominant trends {', '.join(f'{t:.0f} deg' for t in trends)} (structure proxy)")
ax.scatter([], [], marker="s", facecolor="none", edgecolor="#ef4444", label="Top-30% desk-score cells")
ax.scatter([], [], marker="*", s=150, color="#ef4444", label="Desk candidate centre (target at ~50 m depth)")
ax.scatter([], [], marker="o", color="#22c55e", edgecolor="black", label="Provisional collar, arrow = hole azimuth (dip in table)")
ax.plot([], [], color="#f59e0b", lw=4, alpha=0.6, label="R1 cells (20 m)")
ax.set_xlim(view[0], view[1])
ax.set_ylim(view[2], view[3])
ax.set_aspect("equal")
ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
ax.set_title("R1 desk-only drill candidates (no field data) on Sentinel-2 bare-period image\n"
             "UTM 47N (unverified) | contours 10 m from GLO-30", fontsize=11)
ax.annotate("N", xy=(view[1] - 40, view[3] - 30), xytext=(view[1] - 40, view[3] - 100), ha="center",
            fontsize=13, weight="bold", color="white", arrowprops=dict(arrowstyle="-|>", color="white"))
ax.ticklabel_format(useOffset=False, style="plain")
ax.tick_params(labelsize=8)
plt.tight_layout()
fig.savefig(f"{OUT}/r1_desk_candidates_map.png", dpi=200)
plt.close(fig)

# rose of drainage segments (structure proxy)
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(projection="polar")
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
th = np.radians(np.r_[edges[:-1], edges[:-1] + 180] + 5)
ax.bar(th, np.r_[hist, hist], width=np.radians(10), color="#2563eb", alpha=0.75)
ax.set_title("Straight drainage segments, Site 02 DEM\n(length-weighted azimuth)", fontsize=10)
ax.set_yticklabels([])
plt.tight_layout()
fig.savefig(f"{OUT}/dem_drainage_rose.png", dpi=150)
plt.close(fig)

# GPX / KML of targets and provisional collars
gpx = ['<?xml version="1.0" encoding="UTF-8"?>', '<gpx version="1.1" creator="r1_desk_targeting.py" xmlns="http://www.topografix.com/GPX/1/1">']
kml = ['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>R1 desk-only drill candidates</name>']
for c, h in zip(cands.itertuples(), holes.itertuples()):
    desc = f"desk-only target, score {c.score_mean:.2f}; hole az {h.hole_azimuth} dip {h.hole_dip}, {h.planned_depth_m} m"
    gpx.append(f'<wpt lat="{c.lat:.6f}" lon="{c.lon:.6f}"><name>{c.candidate}-target</name><desc>{desc}</desc></wpt>')
    gpx.append(f'<wpt lat="{h.collar_lat}" lon="{h.collar_lon}"><ele>{h.collar_elev}</ele><name>{c.candidate}-collar</name><desc>{desc}</desc></wpt>')
    kml.append(f'<Placemark><name>{c.candidate} target</name><description>{desc}</description><Point><coordinates>{c.lon:.6f},{c.lat:.6f}</coordinates></Point></Placemark>')
    kml.append(f'<Placemark><name>{c.candidate} collar</name><description>{desc}</description><Point><coordinates>{h.collar_lon},{h.collar_lat}</coordinates></Point></Placemark>')
    kml.append(f'<Placemark><name>{c.candidate} hole trace</name><LineString><coordinates>{h.collar_lon},{h.collar_lat} {c.lon:.6f},{c.lat:.6f}</coordinates></LineString></Placemark>')
gpx.append("</gpx>")
kml.append("</Document></kml>")
open(f"{OUT}/r1_desk_candidates.gpx", "w").write("\n".join(gpx))
open(f"{OUT}/r1_desk_candidates.kml", "w").write("\n".join(kml))

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 40)
print(cands.drop(columns="members").round(2).to_string(index=False))
print(holes.to_string(index=False))
print("reference medians:", {k: round(float(cells[f'ref_{k}_p50'].iloc[0]), 3) for k in ('feox', 'fe900', 'clay')})
print(cells[["s2p1_bare_freq", "s2p2_bare_freq", "pct_clay", "pct_feox", "pct_fe900", "dist_lineament_m", "hand_m", "score"]].describe().round(2))
