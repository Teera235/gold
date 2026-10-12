#!/usr/bin/env python3
"""
Multi-date EMIT re-analysis of the R1 cover-review patch (Site 02, Laos).

For every EMIT acquisition over R1 this script reports:
  - cloud / aggregate-mask state of the EMIT pixels that overlap R1 (L2A MASK)
  - L2B MIN group-1 (Fe, ~1 um) and group-2 (~2 um) detections on clear pixels
  - L2B FRCOV fractional cover (green veg / dry veg / bare soil) over R1
  - NDVI where L2A reflectance is available locally
and compares R1 against the rest of the Site 02 AOI, then checks detection
persistence per candidate point C01-C10.

Run with the `geo` conda env:  ~/miniconda3/envs/geo/bin/python analyze_r1_multidate.py
"""

import glob
import json
import os
import re
from collections import Counter, defaultdict

import h5py
import numpy as np
import pandas as pd
import pyproj
import rasterio
from scipy.ndimage import label
from scipy.spatial import cKDTree

DATA = "data"
SITE = "drive-download-20261011T175941Z-1-001"
OUT = "outputs/r1_multidate"
os.makedirs(OUT, exist_ok=True)

TO_UTM = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32647", always_xy=True)
TO_LL = pyproj.Transformer.from_crs("EPSG:32647", "EPSG:4326", always_xy=True)

# EMIT pixel is ~60 m; a swath pixel "overlaps R1" if its centre is within 30 m of an R1 20 m cell centre
R1_OVERLAP_M = 30.0
CANDIDATE_RADIUS_M = 45.0

# ---------------------------------------------------------------- R1 footprint
with rasterio.open(f"{SITE}/02_Maps/historical_cover_disagreement.tif") as ds:
    dis = ds.read(1)
    tr = ds.transform
lbl, _ = label(dis == 1)
ys, xs = np.where(lbl == 90)  # R01, 98 px, 3.92 ha (same patch id as generate_report_visuals.py)
assert len(ys) == 98, f"R1 patch has {len(ys)} px, expected 98"
r1_e = tr.c + (xs + 0.5) * tr.a
r1_n = tr.f + (ys + 0.5) * tr.e
r1_lon, r1_lat = TO_LL.transform(r1_e, r1_n)
r1_tree = cKDTree(np.c_[r1_e, r1_n])

aoi = json.load(open(f"{SITE}/03_Data/manifest.json"))["aoi_coordinates"]
aoi_e, aoi_n = TO_UTM.transform([p[0] for p in aoi], [p[1] for p in aoi])
AOI_BOX = (min(aoi_e), max(aoi_e), min(aoi_n), max(aoi_n))

CANDIDATES = {
    "C10": (18.265105, 101.643454), "C07": (18.265521, 101.643776), "C06": (18.265370, 101.642829),
    "C02": (18.264720, 101.643883), "C01": (18.265805, 101.643138), "C03": (18.266243, 101.643668),
    "C04": (18.265809, 101.644283), "C08": (18.264426, 101.644437), "C05": (18.265146, 101.641828),
    "C09": (18.265531, 101.642254),
}
cand_e, cand_n = TO_UTM.transform([v[1] for v in CANDIDATES.values()], [v[0] for v in CANDIDATES.values()])


def family(name: str) -> str:
    """Group Tetracorder library names into interpretable families."""
    n = name.lower()
    if any(k in n for k in ("grass", "plywood", "lignin", "cellulose", "wood", "vegetation", "leaf", "hay")):
        return "dry_vegetation"
    if any(k in n for k in ("goeth", "hemat", "jaros", "ferrihyd", "lepidocrocite", "fe-hydrox")):
        return "fe_oxide"
    if "dickite" in n:
        return "dickite"
    if "halloy" in n:
        return "halloysite"
    if "kaol" in n:
        return "kaolinite(+mica)"
    if any(k in n for k in ("musc", "illite", "paragon", "sericite", "phengite")):
        return "white_mica"
    if any(k in n for k in ("mont", "smect", "nontron", "beidell", "saponite")):
        return "smectite"
    if "alunite" in n or "pyrophyl" in n:
        return "alunite/pyrophyllite"
    if "calcite" in n or "dolom" in n:
        return "carbonate"
    return "other:" + name.split()[0]


def granule_key(path):
    return re.search(r"(\d{8}T\d{6})", path).group(1) if re.search(r"(\d{8}T\d{6})", path) else None


def find_mask(key, date):
    for p in glob.glob(f"{DATA}/EMIT_L2A_MASK*.nc"):
        if (key and key in p) or os.path.basename(p) == f"EMIT_L2A_MASK_{date.replace('-', '')}.nc":
            return p
    return None


# ---------------------------------------------------------------- per-date L2B MIN
rows, cand_rows, fam_rows = [], [], []
for mpath in sorted(glob.glob(f"{DATA}/EMIT_L2B_MIN_*.nc")):
    key = granule_key(mpath)
    date = f"{key[:4]}-{key[4:6]}-{key[6:8]}"
    f = h5py.File(mpath, "r")
    lat = f["location/lat"][:]
    lon = f["location/lon"][:]
    names = [n.decode() if isinstance(n, bytes) else str(n) for n in f["mineral_metadata/name"][:]]
    idx = f["mineral_metadata/index"][:]
    id2name = {int(i): names[k] for k, i in enumerate(idx)}

    # crop the swath to a box around the AOI before projecting (speed)
    sel = (lat > 18.20) & (lat < 18.32) & (lon > 101.58) & (lon < 101.71)
    if not sel.any():
        continue
    rr, cc = np.where(sel)
    e, n = TO_UTM.transform(lon[rr, cc], lat[rr, cc])
    d_r1, _ = r1_tree.query(np.c_[e, n])
    in_r1 = d_r1 <= R1_OVERLAP_M
    in_aoi = (e >= AOI_BOX[0]) & (e <= AOI_BOX[1]) & (n >= AOI_BOX[2]) & (n <= AOI_BOX[3])

    mpth = find_mask(key, date)
    if mpth:
        mk = h5py.File(mpth, "r")["mask"]
        assert mk.shape[:2] == lat.shape, f"mask/MIN shape mismatch for {date}"
        cloud = mk[:, :, 0][rr, cc]    # Cloud Flag only (what a quick "0% cloud" check reads)
        dil = mk[:, :, 4][rr, cc]      # Dilated Cloud Flag
        aod = mk[:, :, 5][rr, cc]      # AOD550 (smoke / haze)
        agg = mk[:, :, 7][rr, cc]      # Aggregate Flag (1 = do not use)
        spectf = mk[:, :, 9][rr, cc]   # SpecTf ML cloud flag (not part of the aggregate flag)
        nodata = agg == -9999
        # usable = not fill, aggregate flag clear and SpecTf cloud flag clear
        clear = (agg == 0) & (spectf == 0)
    else:
        cloud = dil = aod = spectf = np.full(len(rr), np.nan)
        nodata = np.zeros(len(rr), bool)
        clear = np.ones(len(rr), bool)

    g1 = f["group_1_mineral_id"][:][rr, cc]
    g2 = f["group_2_mineral_id"][:][rr, cc]
    b1 = f["group_1_band_depth"][:][rr, cc]
    b2 = f["group_2_band_depth"][:][rr, cc]

    def fam_counts(m):
        c = Counter()
        for i1, i2 in zip(g1[m], g2[m]):
            if i1 > 0:
                c["g1:" + family(id2name[int(i1)])] += 1
            if i2 > 0:
                c["g2:" + family(id2name[int(i2)])] += 1
        return c

    r1c, aoic = in_r1 & clear, in_aoi & ~in_r1 & clear
    row = {
        "date": date,
        "granule": key,
        "mask_file": os.path.basename(mpth) if mpth else None,
        "r1_emit_px": int(in_r1.sum()),
        "r1_nodata_pct": round(100 * float(nodata[in_r1].mean()), 1),
        "r1_cloudflag_pct": round(100 * float((cloud[in_r1] == 1).mean()), 1),
        "r1_dilated_pct": round(100 * float((dil[in_r1] == 1).mean()), 1),
        "r1_spectf_cloud_pct": round(100 * float((spectf[in_r1] == 1).mean()), 1),
        "r1_aod550": round(float(np.mean(aod[in_r1][aod[in_r1] >= 0])), 2) if (aod[in_r1] >= 0).any() else None,
        "r1_clear_px": int(r1c.sum()),
        "r1_g1_detect_pct": round(100 * float((g1[r1c] > 0).mean()), 1) if r1c.any() else None,
        "r1_g2_detect_pct": round(100 * float((g2[r1c] > 0).mean()), 1) if r1c.any() else None,
        "aoi_clear_px": int(aoic.sum()),
        "aoi_g1_detect_pct": round(100 * float((g1[aoic] > 0).mean()), 2) if aoic.any() else None,
        "aoi_g2_detect_pct": round(100 * float((g2[aoic] > 0).mean()), 2) if aoic.any() else None,
        "r1_g1_bd_max": round(float(b1[r1c].max()), 3) if r1c.any() else None,
        "r1_g2_bd_max": round(float(b2[r1c].max()), 3) if r1c.any() else None,
    }
    rows.append(row)
    for fam, cnt in fam_counts(r1c).items():
        fam_rows.append({"date": date, "where": "R1", "family": fam, "px": cnt, "share": cnt / max(r1c.sum(), 1)})
    for fam, cnt in fam_counts(aoic).items():
        fam_rows.append({"date": date, "where": "AOI_excl_R1", "family": fam, "px": cnt, "share": cnt / max(aoic.sum(), 1)})

    # candidate points: nearest swath pixel (any mask state) within CANDIDATE_RADIUS_M
    tree = cKDTree(np.c_[e, n])
    for cid, ce, cn in zip(CANDIDATES, cand_e, cand_n):
        d, j = tree.query([ce, cn])
        if d > CANDIDATE_RADIUS_M:
            continue
        cand_rows.append({
            "date": date, "id": cid, "emit_pixel": f"{rr[j]}_{cc[j]}", "dist_m": round(float(d), 1),
            "clear": bool(clear[j]),
            "g1": id2name.get(int(g1[j]), "-") if g1[j] > 0 else "-", "g1_bd": round(float(b1[j]), 3),
            "g2": id2name.get(int(g2[j]), "-") if g2[j] > 0 else "-", "g2_bd": round(float(b2[j]), 3),
            "g1_family": family(id2name[int(g1[j])]) if g1[j] > 0 else "-",
            "g2_family": family(id2name[int(g2[j])]) if g2[j] > 0 else "-",
        })

summary = pd.DataFrame(rows).sort_values("date")
fams = pd.DataFrame(fam_rows)
cands = pd.DataFrame(cand_rows)

# ---------------------------------------------------------------- FRCOV (orthorectified GeoTIFFs, EPSG:4326)
fr_rows = []
for bare in sorted(glob.glob(f"{DATA}/frcov/EMIT_L2B_FRCOVBARE_*.tif")):
    key = granule_key(bare)
    date = f"{key[:4]}-{key[4:6]}-{key[6:8]}"
    vals = {}
    for comp in ("PV", "NPV", "BARE"):
        with rasterio.open(bare.replace("FRCOVBARE", "FRCOV" + comp)) as ds:
            v = np.array([s[0] for s in ds.sample(zip(r1_lon, r1_lat))], float)
            v[v == ds.nodata] = np.nan
            vals[comp] = v
            # AOI context: read a window over the AOI bbox
            win = rasterio.windows.from_bounds(101.6098, 18.2302, 101.6763, 18.2873, ds.transform)
            a = ds.read(1, window=win).astype(float)
            a[a == ds.nodata] = np.nan
            vals["AOI_" + comp] = a
    valid = np.isfinite(vals["BARE"])
    fr_rows.append({
        "date": date,
        "r1_valid_cells": int(valid.sum()),
        "r1_green_veg": round(float(np.nanmean(vals["PV"])), 3) if valid.any() else None,
        "r1_dry_veg": round(float(np.nanmean(vals["NPV"])), 3) if valid.any() else None,
        "r1_bare_soil": round(float(np.nanmean(vals["BARE"])), 3) if valid.any() else None,
        "r1_bare_max": round(float(np.nanmax(vals["BARE"])), 3) if valid.any() else None,
        "aoi_green_veg": round(float(np.nanmean(vals["AOI_PV"])), 3),
        "aoi_bare_soil": round(float(np.nanmean(vals["AOI_BARE"])), 3),
        "aoi_valid_share": round(float(np.isfinite(vals["AOI_BARE"]).mean()), 3),
    })
frcov = pd.DataFrame(fr_rows)

# ---------------------------------------------------------------- NDVI from locally available reflectance
ndvi_rows = []
for rpath in sorted(glob.glob(f"{DATA}/EMIT_L2A_RFL_*.nc")):
    key = granule_key(rpath)
    f = h5py.File(rpath, "r")
    wl = f["sensor_band_parameters/wavelengths"][:]
    lat, lon = f["location/lat"][:], f["location/lon"][:]
    sel = (lat > 18.262) & (lat < 18.270) & (lon > 101.639) & (lon < 101.648)
    rr, cc = np.where(sel)
    e, n = TO_UTM.transform(lon[rr, cc], lat[rr, cc])
    m = r1_tree.query(np.c_[e, n])[0] <= R1_OVERLAP_M
    red = f["reflectance"][:, :, int(np.argmin(abs(wl - 660)))][rr[m], cc[m]]
    nir = f["reflectance"][:, :, int(np.argmin(abs(wl - 860)))][rr[m], cc[m]]
    ndvi = (nir - red) / (nir + red)
    ndvi_rows.append({"date": f"{key[:4]}-{key[4:6]}-{key[6:8]}", "r1_emit_px": int(m.sum()),
                      "ndvi_median": round(float(np.median(ndvi)), 3), "ndvi_min": round(float(ndvi.min()), 3),
                      "ndvi_max": round(float(ndvi.max()), 3),
                      "px_ndvi_le_0.35": int((ndvi <= 0.35).sum())})
ndvi = pd.DataFrame(ndvi_rows)


# ---------------------------------------------------------------- control: R1 vs other bare ground
def fam3(name):
    n = name.lower()
    if any(k in n for k in ("kaol", "halloy", "dickite", "nacrite")):
        return "kaolin"
    if any(k in n for k in ("goeth", "jaros", "hemat", "ferrihyd", "fe-hydrox")):
        return "fe"
    if any(k in n for k in ("musc", "illite", "paragon")):
        return "mica"
    return "other"


ctrl_rows = []
BOXES = {"AOI_43km2": (18.230, 18.288, 101.609, 101.677), "box_20km": (18.17, 18.36, 101.55, 101.74)}
for rpath in sorted(glob.glob(f"{DATA}/EMIT_L2A_RFL_*.nc")):
    key = granule_key(rpath)
    mins = glob.glob(f"{DATA}/EMIT_L2B_MIN_*{key}*.nc")
    msk = glob.glob(f"{DATA}/EMIT_L2A_MASK_*{key}*.nc")
    if not (mins and msk):
        continue
    R, M, Q = h5py.File(rpath, "r"), h5py.File(mins[0], "r"), h5py.File(msk[0], "r")["mask"]
    lat, lon = R["location/lat"][:], R["location/lon"][:]
    wl = R["sensor_band_parameters/wavelengths"][:]
    md = M["mineral_metadata"]
    nm = {int(i): x.decode() for i, x in zip(md["index"][:], md["name"][:])}
    for bname, b in BOXES.items():
        rr, cc = np.where((lat > b[0]) & (lat < b[1]) & (lon > b[2]) & (lon < b[3]))
        red = R["reflectance"][:, :, int(np.argmin(abs(wl - 660)))][rr, cc]
        nir = R["reflectance"][:, :, int(np.argmin(abs(wl - 860)))][rr, cc]
        nd = (nir - red) / (nir + red)
        ok = (Q[:, :, 7][rr, cc] == 0) & (Q[:, :, 9][rr, cc] == 0)
        e, n = TO_UTM.transform(lon[rr, cc], lat[rr, cc])
        inr1 = r1_tree.query(np.c_[e, n])[0] <= R1_OVERLAP_M
        f1 = np.array([fam3(nm[i]) if i > 0 else "-" for i in M["group_1_mineral_id"][:][rr, cc]])
        f2 = np.array([fam3(nm[i]) if i > 0 else "-" for i in M["group_2_mineral_id"][:][rr, cc]])
        for gname, g in (("R1", inr1 & ok),
                         ("bare_ndvi<=0.35_excl_R1", (nd <= 0.35) & ~inr1 & ok),
                         ("bare_ndvi<=0.25_excl_R1", (nd <= 0.25) & ~inr1 & ok)):
            if g.sum() == 0:
                continue
            ctrl_rows.append({"date": f"{key[:4]}-{key[4:6]}-{key[6:8]}", "box": bname, "group": gname, "n_px": int(g.sum()),
                              "fe_pct": round(100 * float((f1[g] == "fe").mean()), 1),
                              "kaolin_pct": round(100 * float((f2[g] == "kaolin").mean()), 1),
                              "mica_pct": round(100 * float((f2[g] == "mica").mean()), 1),
                              "fe_and_kaolin_pct": round(100 * float(((f1[g] == "fe") & (f2[g] == "kaolin")).mean()), 1)})
control = pd.DataFrame(ctrl_rows).drop_duplicates(subset=["date", "group", "n_px"])

# ---------------------------------------------------------------- persistence per candidate
persist = []
if not cands.empty:
    for cid, g in cands[cands.clear].groupby("id"):
        persist.append({
            "id": cid,
            "clear_dates": len(g),
            "fe_oxide_dates": int((g.g1_family == "fe_oxide").sum()),
            "clay_mica_dates": int(g.g2_family.isin(["kaolinite(+mica)", "white_mica", "halloysite", "dickite"]).sum()),
            "dickite_dates": int((g.g2_family == "dickite").sum()),
            "dry_veg_dates": int((g.g2_family == "dry_vegetation").sum()),
            "no_g2_detect_dates": int((g.g2 == "-").sum()),
            "distinct_emit_pixels_used": g.emit_pixel.nunique(),
        })
persist = pd.DataFrame(persist)

# pixels shared between candidates (same EMIT pixel on the same date)
shared = (cands.groupby(["date", "emit_pixel"]).id.apply(lambda s: ",".join(sorted(s)))
          .reset_index().query("id.str.contains(',')", engine="python") if not cands.empty else pd.DataFrame())

# ---------------------------------------------------------------- write + print
summary.to_csv(f"{OUT}/r1_per_date_summary.csv", index=False)
fams.to_csv(f"{OUT}/r1_vs_aoi_mineral_families.csv", index=False)
cands.to_csv(f"{OUT}/r1_candidates_per_date.csv", index=False)
persist.to_csv(f"{OUT}/r1_candidate_persistence.csv", index=False)
frcov.to_csv(f"{OUT}/r1_fractional_cover.csv", index=False)
ndvi.to_csv(f"{OUT}/r1_ndvi.csv", index=False)
control.to_csv(f"{OUT}/r1_vs_bare_ground_control.csv", index=False)
shared.to_csv(f"{OUT}/r1_candidates_sharing_emit_pixel.csv", index=False)

pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)
print("=== Per-date L2B MIN over R1 (clear = not fill, Aggregate Flag 0 and SpecTf cloud flag 0) ===\n", summary.to_string(index=False))
print("\n=== Mineral families on clear pixels: R1 vs rest of AOI (share of clear px) ===")
if not fams.empty:
    print(fams.pivot_table(index="family", columns=["where", "date"], values="share").round(3).fillna(0).to_string())
print("\n=== Fractional cover over R1 (EMIT L2B FRCOV) ===\n", frcov.to_string(index=False))
print("\n=== NDVI over R1 (local L2A RFL) ===\n", ndvi.to_string(index=False))
print("\n=== Control: R1 vs other bare ground (clear px, L2B families) ===\n", control.to_string(index=False))
print("\n=== Candidate persistence across clear dates ===\n", persist.to_string(index=False))
print("\n=== Candidates sharing one EMIT pixel on the same date ===\n", shared.to_string(index=False))
print(f"\nWrote CSVs to {OUT}/")
