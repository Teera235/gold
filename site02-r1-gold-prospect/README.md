# Site 02 (Sangthong, Laos) - R1 gold prospect: remote-sensing analysis and drill planning

Working repository for the R1 / R01 patch (3.92 ha, centre ~18.2658 N, 101.6438 E; UTM 47N 779,540 E / 2,021,620 N).
It holds every report, script and result produced so far. Raw satellite downloads (5+ GB) are **not** stored here;
the scripts re-download them (see [Reproducing](#reproducing)).

> Coordinates use WGS 84 / UTM 47N (EPSG:32647). This CRS was **assumed** from the original coordinate image and must be
> verified with GNSS on site before navigation or drilling.

## Start here

| Read | What it gives you |
|---|---|
| [R1_DESK_DRILL_CANDIDATES.md](R1_DESK_DRILL_CANDIDATES.md) | **Latest.** Four desk-only scout-hole candidates (DT-1 to DT-4) with collars, azimuth/dip and reasons; free data used; where to buy hyperspectral / SWIR imagery |
| [R1_DRILL_SITE_SELECTION_PLAN.md](R1_DRILL_SITE_SELECTION_PLAN.md) | Field program for choosing collars from on-site evidence: soil grid, traverses, drainage sampling, go/no-go rules |
| [R1_MULTIDATE_REANALYSIS.md](R1_MULTIDATE_REANALYSIS.md) | EMIT across 8 dates: which scenes are usable, mineral persistence, R1 vs regional bare ground, surface-cover trend |
| [HYPERSPECTRAL_GOLD_RESEARCH.md](HYPERSPECTRAL_GOLD_RESEARCH.md) | Literature review: what hyperspectral can and cannot show for gold, alteration models, tropical limitations |

**Superseded (kept for history):** [R1_CANDIDATE_EXPLORATION_PLAN.md](R1_CANDIDATE_EXPLORATION_PLAN.md),
[r1_candidates_report.html](r1_candidates_report.html), `visuals/`, [generate_report_visuals.py](generate_report_visuals.py).
These were based on a single 2025-01-22 EMIT scene; their drill holes and C01-C10 ranking are replaced by the documents above.

## Progress so far

1. **Site 02 package** (`drive-download-20261011T175941Z-1-001/`): Sentinel-2 screening of the 43 km² AOI delivered
   10 Oct 2026 - no anomaly zone passed; R01-R10 flagged as cover-review areas.
2. **Notebook 15** (`15_laos_emit_transfer.ipynb`): Nevada-trained gold models transferred to EMIT over Laos - null result
   (user box is forest; out-of-domain). Paths inside refer to the original RIFFAI_GOLD repo and will not run here as-is.
3. **EMIT multi-date re-analysis**: kaolinite + Fe-oxide at R1 is repeatable but matches regional bare soil; dickite/halloysite
   were single-pixel, single-date; R1 is revegetating.
4. **Field plan + field pack** for on-site work (`outputs/r1_field/`).
5. **Desk-only drill candidates** from Sentinel-2 (bare period Dec 2024 - May 2025), EMIT, DEM: DT-1 and DT-2 are robust;
   DT-2 + DT-4 can share one pad.
6. **Imagery sourcing**: WorldView-3 SWIR, PRISMA, Tanager archive searches recommended for Dec 2024 - Apr 2025.

## Repository layout

| Path | Contents |
|---|---|
| `*.md` | Reports (above) |
| `outputs/r1_desk/` | Desk candidates: GPX/KML/CSV, maps, per-cell evidence |
| `outputs/r1_field/` | Field pack: 40 m soil grid, traverses, drainage points, pad-feasible cells, GPX/KML, map |
| `outputs/r1_multidate/` | EMIT multi-date tables |
| `drive-download-20261011T175941Z-1-001/` | Original Site 02 delivery package (reports, GeoTIFFs, field forms, notebook) |
| `15_laos_emit_transfer.ipynb` | Experiment 15 notebook with outputs |
| `download_emit.py` | Search / download EMIT granules from NASA CMR (needs Earthdata token) |
| `analyze_r1_multidate.py` | EMIT multi-date analysis -> `outputs/r1_multidate/` |
| `make_r1_field_pack.py` | Field pack -> `outputs/r1_field/` |
| `fetch_s2_r1.py` | Sentinel-2 L2A windows around R1 from Microsoft Planetary Computer (free, no account) |
| `r1_desk_targeting.py` | Desk-only candidate ranking -> `outputs/r1_desk/` |
| `r1_collar_calc.py` | Collar position / azimuth / length from a measured structure |

For the field team: load `outputs/r1_field/r1_field_pack.gpx` and `outputs/r1_desk/r1_desk_candidates.gpx` on GPS units
or phones (OsmAnd, Gaia, Avenza, Garmin); open the `.kml` files in Google Earth.

## Reproducing

```bash
conda create -n geo python=3.12 && conda activate geo
pip install -r requirements.txt

# NASA Earthdata token (https://urs.earthdata.nasa.gov -> Generate Token), never commit this file
echo 'NASA_FETCH=<your token>' > .env

# EMIT mineral maps, masks, reflectance over R1 (writes to data/)
python download_emit.py --lat 18.265841 --lon 101.643824 --product mineral --list
python download_emit.py --lat 18.265841 --lon 101.643824 --product mineral --date 2026-01-25
python download_emit.py --lat 18.265841 --lon 101.643824 --product mask --date 2026-01-25
#   repeat for 2025-01-22, 2026-01-21, 2026-04-16, 2026-04-20, 2026-04-24, 2026-04-28, 2026-05-25;
#   reflectance (--product reflectance, ~1.8 GB each) for 2025-01-22 and 2026-01-25.
#   EMIT fractional cover: search CMR short_name=EMITL2BFRCOV version=001 at the same point and download the
#   FRCOVPV/NPV/BARE/QC GeoTIFFs (Bearer token) into data/frcov/.
#   ASTER AST_07XT (optional, negative result) goes in data/aster/.

python fetch_s2_r1.py            # Sentinel-2 windows -> data/s2_r1/ (~86 MB, ~20 min)
python analyze_r1_multidate.py
python make_r1_field_pack.py
python r1_desk_targeting.py
python r1_collar_calc.py --e 779540 --n 2021560 --dipdir 120 --dip 65 --depth 50
```

## Data sources

NASA EMIT L2A/L2B (LP DAAC), Sentinel-2 L2A (Copernicus, via Microsoft Planetary Computer), ASTER AST_07XT (LP DAAC),
Copernicus GLO-30 DEM, ESA WorldCover 2021. All results are **unvalidated reconnaissance**: no field samples or assays exist yet.
