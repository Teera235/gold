#!/usr/bin/env python3
"""
Download a 3 x 3 km Sentinel-2 L2A window around R1 for every scene (Oct 2024 - Oct 2026, tile cloud < 40%)
from Microsoft Planetary Computer (free, anonymous SAS token). Saves data/s2_r1/<scene>.npz with
B02,B03,B04,B05,B08,B8A,B11,B12 (reflectance, offset applied) and SCL, all on a 10 m UTM 47N grid.

Run with: ~/miniconda3/envs/geo/bin/python fetch_s2_r1.py
"""

import json
import os
import urllib.request

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import from_bounds

OUT = "data/s2_r1"
os.makedirs(OUT, exist_ok=True)
CX, CY, HALF = 779540, 2021580, 1500
BOUNDS = (CX - HALF, CY - HALF, CX + HALF, CY + HALF)
NPX = 2 * HALF // 10
BANDS = ["B02", "B03", "B04", "B05", "B08", "B8A", "B11", "B12", "SCL"]
STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search"


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


body = {"collections": ["sentinel-2-l2a"], "bbox": [101.640, 18.263, 101.647, 18.268],
        "datetime": "2024-10-01/2026-10-12", "limit": 200, "query": {"eo:cloud_cover": {"lt": 40}}}
items = post(STAC, body)["features"]
token = json.load(urllib.request.urlopen(
    "https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a"))["token"]

env = rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", GDAL_HTTP_MULTIRANGE="YES", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif")
with env:
    for it in sorted(items, key=lambda x: x["properties"]["datetime"]):
        sid = it["id"]
        dst = f"{OUT}/{sid}.npz"
        if os.path.exists(dst):
            continue
        baseline = float(it["properties"].get("s2:processing_baseline", "0") or 0)
        offset = -1000 if baseline >= 4.0 else 0
        arrs = {}
        try:
            for b in BANDS:
                href = it["assets"][b]["href"] + "?" + token
                with rasterio.open(href) as ds:
                    assert ds.crs.to_epsg() == 32647, ds.crs
                    w = from_bounds(*BOUNDS, ds.transform)
                    a = ds.read(1, window=w, out_shape=(NPX, NPX),
                                resampling=Resampling.nearest if b == "SCL" else Resampling.bilinear)
                arrs[b] = a.astype(np.uint8) if b == "SCL" else ((a.astype(np.float32) + offset) / 10000.0)
            np.savez_compressed(dst, date=it["properties"]["datetime"][:10], bounds=np.array(BOUNDS), **arrs)
            scl = arrs["SCL"]
            print(sid[:24], it["properties"]["datetime"][:10], f"clear-land {np.isin(scl, [4, 5]).mean():.2f}", flush=True)
        except Exception as e:  # keep going on transient HTTP errors
            print("FAIL", sid, e, flush=True)
