#!/usr/bin/env python3
"""
NASA EMIT Hyperspectral Data Fetcher
Fetches NASA EMIT (Hyperspectral Imaging Spectrometer) data for a given coordinate.
Uses NASA Common Metadata Repository (CMR) API and Earthdata token for authenticated downloads.
"""

import os
import sys
import argparse
import urllib.request
import urllib.error
import json
from pathlib import Path


def load_token(env_path=".env") -> str:
    """Read Earthdata Bearer Token from .env file."""
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Configuration file '{env_path}' not found.")
    
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key in ("NASA_FETCH", "EARTHDATA_TOKEN", "NASA_TOKEN"):
                    return val
    raise ValueError(f"No valid token found in {env_path} (expected NASA_FETCH or EARTHDATA_TOKEN).")


def search_granules(lat: float, lon: float, short_name: str, limit: int = 50):
    """
    Search granules from NASA CMR API for a point coordinate.
    CMR point parameter format: point=lon,lat
    """
    point_str = f"{lon},{lat}"
    url = f"https://cmr.earthdata.nasa.gov/search/granules.json?short_name={short_name}&point={point_str}&page_size={limit}&sort_key=-start_date"
    req = urllib.request.Request(url, headers={"User-Agent": "NASA-EMIT-Fetcher/1.0"})
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    entries = data.get("feed", {}).get("entry", [])
    results = []
    for e in entries:
        title = e.get("title")
        time_start = e.get("time_start", "")
        cloud_cover = e.get("cloud_cover", 100)
        
        # Extract download URL (.nc file)
        nc_url = None
        for link in e.get("links", []):
            href = link.get("href", "")
            if href.endswith(".nc") and "lp-prod-protected" in href:
                nc_url = href
                break
        
        if nc_url:
            results.append({
                "title": title,
                "time_start": time_start,
                "cloud_cover": float(cloud_cover) if cloud_cover is not None else 100.0,
                "download_url": nc_url,
                "short_name": short_name
            })
    return results


class CustomRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Handle redirects from NASA Earthdata to CloudFront / S3 pre-signed URLs."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Create a new request to follow the redirect
        new_req = urllib.request.Request(newurl)
        return new_req


def download_file(url: str, dest_path: Path, token: str, max_retries: int = 10):
    """Download a protected NASA file with Bearer token authentication, resume capability, and retries."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dest_path.with_suffix(dest_path.suffix + ".part")
    opener = urllib.request.build_opener(CustomRedirectHandler)
    
    # Get total remote size via HEAD/initial GET
    initial_req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "NASA-EMIT-Fetcher/1.0"
    })
    
    with opener.open(initial_req) as resp:
        total_size = int(resp.headers.get("Content-Length", 0))
    
    total_mb = total_size / (1024 * 1024) if total_size > 0 else 0
    print(f"\n[Connecting] {dest_path.name}")
    print(f"[Target Size] {total_mb:.2f} MB")
    
    for attempt in range(max_retries):
        existing_size = temp_path.stat().st_size if temp_path.exists() else 0
        if total_size > 0 and existing_size >= total_size:
            break
        
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "NASA-EMIT-Fetcher/1.0"
        }
        if existing_size > 0:
            headers["Range"] = f"bytes={existing_size}-"
            print(f"\n[Resuming from {existing_size / (1024*1024):.2f} MB ({existing_size/total_size*100:.1f}%)]")
        
        req = urllib.request.Request(url, headers=headers)
        try:
            with opener.open(req) as resp:
                status = getattr(resp, "status", 200)
                # If server doesn't support Range and sends 200 instead of 206, write from start
                mode = "ab" if (existing_size > 0 and status == 206) else "wb"
                downloaded = existing_size if (existing_size > 0 and status == 206) else 0
                
                block_size = 2 * 1024 * 1024  # 2MB chunks
                with open(temp_path, mode) as f:
                    while True:
                        chunk = resp.read(block_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            downloaded_mb = downloaded / (1024 * 1024)
                            print(f"\r  -> Progress: {percent:5.1f}% [{downloaded_mb:.2f}/{total_mb:.2f} MB]", end="", flush=True)
                        else:
                            downloaded_mb = downloaded / (1024 * 1024)
                            print(f"\r  -> Downloaded: {downloaded_mb:.2f} MB", end="", flush=True)
            
            # Check if finished
            current_size = temp_path.stat().st_size if temp_path.exists() else 0
            if total_size > 0 and current_size >= total_size:
                break
            elif total_size > 0:
                print(f"\n[Warning] Connection closed at {current_size / (1024*1024):.2f}/{total_mb:.2f} MB. Retrying (attempt {attempt+1}/{max_retries})...")
        except Exception as err:
            print(f"\n[Network Error] {err}. Retrying (attempt {attempt+1}/{max_retries})...")
            import time
            time.sleep(2)
            
    # Final check
    final_size = temp_path.stat().st_size if temp_path.exists() else 0
    if total_size > 0 and final_size < total_size:
        raise RuntimeError(f"Download incomplete: {final_size} / {total_size} bytes after {max_retries} attempts.")
        
    temp_path.replace(dest_path)
    print("\n[Done] Saved to:", dest_path.resolve())


def main():
    parser = argparse.ArgumentParser(description="Fetch NASA EMIT Hyperspectral Data by Coordinates")
    parser.add_argument("--lat", type=float, default=18.2633746, help="Latitude (default: 18.2633746)")
    parser.add_argument("--lon", type=float, default=101.6413906, help="Longitude (default: 101.6413906)")
    parser.add_argument("--product", type=str, choices=["mineral", "reflectance", "mask", "all"], default="mineral",
                        help="Data product to download: mineral (EMITL2BMIN ~39MB), reflectance (EMITL2ARFL ~1.7GB), mask (EMITL2AMASK ~15MB)")
    parser.add_argument("--list", action="store_true", help="List all available dates and exit without downloading")
    parser.add_argument("--max-cloud", type=float, default=None, help="Filter scenes with cloud cover <= max-cloud percent")
    parser.add_argument("--latest", action="store_true", help="Download the most recent scene (regardless of cloud cover)")
    parser.add_argument("--date", type=str, default=None, help="Download scene for a specific date (YYYY-MM-DD)")
    parser.add_argument("--index", type=int, default=None, help="Download scene by index number from the list (1-based)")
    parser.add_argument("--best", action="store_true", default=False, help="Download scene with lowest cloud cover")
    parser.add_argument("--outdir", type=str, default="./data", help="Output directory for downloaded files")
    
    args = parser.parse_args()
    
    # Mapping friendly product names to NASA collection short names
    product_map = {
        "mineral": "EMITL2BMIN",
        "reflectance": "EMITL2ARFL",
        "mask": "EMITL2AMASK"
    }
    
    target_short_name = product_map.get(args.product, "EMITL2BMIN")
    
    print(f"=== NASA EMIT Hyperspectral Search ===")
    print(f"Coordinates: Lat {args.lat}, Lon {args.lon}")
    print(f"Searching collection: {target_short_name}...")
    
    granules = search_granules(args.lat, args.lon, target_short_name)
    if not granules:
        print("No granules found for the specified coordinate.")
        return
    
    if args.max_cloud is not None:
        granules = [g for g in granules if g["cloud_cover"] <= args.max_cloud]
        if not granules:
            print(f"No scenes found with cloud cover <= {args.max_cloud}%.")
            return
    
    print(f"\nFound {len(granules)} scenes covering this location (Sorted newest to oldest):")
    print(f"{'-'*75}")
    print(f"{'Idx':<4} | {'Date':<10} | {'Time (UTC)':<10} | {'Cloud %':<8} | {'Granule ID'}")
    print(f"{'-'*75}")
    for idx, g in enumerate(granules):
        date_str = g['time_start'][:10]
        time_str = g['time_start'][11:19]
        print(f"[{idx+1:2d}] | {date_str} | {time_str} | {g['cloud_cover']:6.1f}% | {g['title']}")
    print(f"{'-'*75}")
    
    if args.list:
        return
    
    token = load_token()
    
    selected_scene = None
    if args.index is not None:
        if 1 <= args.index <= len(granules):
            selected_scene = granules[args.index - 1]
        else:
            print(f"Error: Invalid index {args.index}. Must be between 1 and {len(granules)}.")
            return
    elif args.date is not None:
        matching = [g for g in granules if g["time_start"].startswith(args.date)]
        if matching:
            selected_scene = matching[0]
        else:
            print(f"Error: No scene found matching date '{args.date}'.")
            return
    elif args.latest:
        selected_scene = granules[0]
    elif args.best:
        selected_scene = sorted(granules, key=lambda x: x["cloud_cover"])[0]
    else:
        # Default behavior: recommend best, but if user asked without flags, pick best
        selected_scene = sorted(granules, key=lambda x: x["cloud_cover"])[0]
    
    print(f"\nSelected scene: {selected_scene['title']}")
    print(f"Acquired date: {selected_scene['time_start'][:10]} | Cloud: {selected_scene['cloud_cover']}%")
    
    out_dir = Path(args.outdir)
    filename = selected_scene["download_url"].split("/")[-1]
    dest_path = out_dir / filename
    
    if dest_path.exists():
        # Verify if existing file is complete
        try:
            opener = urllib.request.build_opener(CustomRedirectHandler)
            chk_req = urllib.request.Request(selected_scene["download_url"], headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "NASA-EMIT-Fetcher/1.0"
            })
            with opener.open(chk_req) as r:
                expected_size = int(r.headers.get("Content-Length", 0))
            if expected_size > 0 and dest_path.stat().st_size >= expected_size:
                print(f"\n[Info] Complete file already exists ({dest_path.stat().st_size / (1024*1024):.2f} MB): {dest_path}")
                return
            else:
                print(f"\n[Info] Incomplete file detected ({dest_path.stat().st_size / (1024*1024):.2f} MB of {expected_size / (1024*1024):.2f} MB). Moving to .part to resume...")
                temp_path = dest_path.with_suffix(dest_path.suffix + ".part")
                dest_path.replace(temp_path)
        except Exception:
            pass
    
    download_file(selected_scene["download_url"], dest_path, token)


if __name__ == "__main__":
    main()
