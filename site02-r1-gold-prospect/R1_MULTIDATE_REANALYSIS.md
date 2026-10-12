# R1 Patch — Multi-date EMIT Re-analysis

**Site:** Site 02, Sangthong (Laos) · **Target:** R1 / R01 cover-review patch, 3.92 ha (98 cells at 20 m), centre 779,540 E / 2,021,620 N (UTM 47N, CRS still unverified in the field)
**Replaces:** the single-date (2025-01-22) mineral interpretation in `R1_CANDIDATE_EXPLORATION_PLAN.md` and `r1_candidates_report.html`
**Reproduce:** `~/miniconda3/envs/geo/bin/python analyze_r1_multidate.py` → tables in `outputs/r1_multidate/`

---

## 1. Bottom line

1. **Only two of the eight EMIT dates over R1 are clean, and the newest clean one is 2026-01-25.** The other late-2026 scenes are unusable over R1. This includes 2026-04-24, which had been recommended as the best date: it has **no data** over R1.
2. **Kaolinite (± muscovite) with goethite/jarosite is a real, repeatable signal at R1.** It appears on every date where the surface is visible.
3. **That signal does not make R1 special.** On 2026-01-25, the truly bare pixels within ~20 km show the same assemblage at about the same rate: 81% Fe-oxide, 70% kaolin, 69% both, against R1's 80% / 100% / 80%. This is the normal signature of exposed tropical soil and saprolite. It is not specific to hydrothermal alteration.
4. **Halloysite and dickite were one pixel each on one date** (2025-01-22). Neither appears in R1 on any of the seven later dates. They cannot support targets C07 or C03.
5. **R1's bare surface is disappearing.** EMIT fractional cover gives bare soil at 54–65% of R1 in Jan–Mar 2025, 7–9% in Jan 2026, and about 0% in Apr–May 2026, while dry and green vegetation increase. This pattern fits a clearing that is revegetating.
6. **The drill-hole proposals (DH-R1-01/02/03) are not supported** by the multi-date data. R1 is still a reasonable place for a field visit and soil/rock sampling.

---

## 2. Date-by-date quality over R1

"Usable" means the EMIT pixel is not fill, the L2A Aggregate Flag is 0, and the SpecTf ML cloud flag is 0. The SpecTf flag is not included in the Aggregate Flag, so it is checked separately.

| Date | Cloud Flag only | What actually affects R1 | Usable EMIT px / total | Verdict |
|---|---|---|---|---|
| 2025-01-22 | 0% | clean, AOD 0.34 | **16 / 16** | ✅ usable |
| 2026-01-21 | 0% | **Dilated-cloud flag on 100% of R1** | 0 / 15 | ⚠️ cloud edge; minerals match 2025-01-22 but are not quality-controlled |
| 2026-01-25 | 0% | SpecTf cloud flag on 67% of R1 | **5 / 15** | ✅ usable (5 px) |
| 2026-04-16 | 0% | Dilated cloud 83%, **AOD 0.66** (burning-season haze) | 0 / 18 | ❌ |
| 2026-04-20 | 0% | SpecTf cloud 38%, AOD 0.45 | 10 / 16 | ❌ in practice: matches are non-physical (§3) |
| 2026-04-24 | 0% | **Mask is fill (−9999): no data over R1**; L2B has zero detections | 0 / 14 | ❌ no data |
| 2026-04-28 | 0% | SpecTf cloud 63%, AOD 0.76 | 0 / 16 | ❌ |
| 2026-05-25 | 0% | Dilated cloud 100%, SpecTf 93% | 0 / 14 | ❌ |

**Why the "0% cloud, 100% bare" table was misleading:**
- It used only the basic Cloud Flag. That flag is 0 on every date, including dates where R1 is cloud edge, haze, ML-detected cloud or no data.
- "Cloud-free" was read as "100% bare soil". Cloud cover and bare soil are separate measurements. For bare soil, see §4.

---

## 3. Minerals detected at R1 (EMIT L2B MIN, pixels overlapping R1)

| Date | Group 1 (Fe, ~1 µm) | Group 2 (~2 µm) | Comment |
|---|---|---|---|
| 2025-01-22 | Goethite+qtz+jarosite 44% | Kaol+muscovite 63%, muscovite 13%, nacrite 6% | Original single-date basis of the R1 plan |
| 2026-01-21* | Goethite/jarosite, ferrihydrite | Kaol+muscovite (10 of 15 px) | Same pattern; not QC-clean |
| 2026-01-25 | Fe-oxide 80% | Kaol+muscovite 100% | Same pattern; band depth up to 0.19 |
| 2026-04-16* | Amorphous Fe-hydroxide | Kaol+muscovite (14 of 18 px) | Same pattern under haze |
| 2026-04-20 | Fe-hydroxide 30% | **Mg-perchlorate 63%**, cronstedtite 19%, kaol 20% | Non-physical library matches → spectra degraded by haze/cloud |
| 2026-05-25* | Goethite thin film | **Witherite**, perchlorate | Non-physical; cloudy |

\* not QC-clean; shown only to test whether the signal persists.

- **What persists:** kaolinite + muscovite + Fe-oxide, across two dry seasons.
- **What does not persist:**
  - Halloysite (band depth 0.159) and dickite (0.059): one pixel each on 2025-01-22, and absent on all seven later dates.
  - The "advanced-argillic / epithermal" reading built on dickite.

### Control: is R1 different from other bare ground?

The table counts clear pixels only. "Bare" means EMIT NDVI ≤ 0.25 or ≤ 0.35, excluding R1.

| Date | Group | n px | Fe-oxide | Kaolin | Fe + kaolin |
|---|---|---|---|---|---|
| 2025-01-22 | **R1** | 16 | 44% | 69% | 44% |
| 2025-01-22 | bare (NDVI ≤ 0.25), 20 km box | 688 | 45% | 13% | 12% |
| 2026-01-25 | **R1** | 5 | 80% | 100% | 80% |
| 2026-01-25 | bare (NDVI ≤ 0.25), 20 km box | 581 | 81% | 70% | 69% |

- **2025 data:** R1 was more kaolinitic than other bare ground.
- **2026 data (newer):** R1 matches bare ground in general.

Kaolinite and goethite are the dominant minerals of lateritic soil and saprolite across tropical SE Asia. Their presence alone does not separate hydrothermal alteration from ordinary weathering. Separating the two would need minerals or features that EMIT did not reproducibly detect here: alunite, pyrophyllite, well-ordered dickite, or white-mica 2200 nm position zoning. It would also need ground truth.

Compared with the whole AOI, R1 still stands out: about 40–80% Fe-oxide vs 0.2–3%. This happens because R1 is one of the few places where soil is visible at all; the AOI is ~96% forest.

---

## 4. Surface cover at R1 (EMIT L2B FRCOV, mean over 98 R1 cells)

| Date | Green veg | Dry veg | **Bare soil** |
|---|---|---|---|
| 2025-01-22 | 0.37 | 0.09 | **0.54** |
| 2025-02-14 | 0.37 | 0.07 | **0.57** |
| 2025-03-24 | 0.07 | 0.28 | **0.65** |
| 2026-01-21 | 0.30 | 0.60 | **0.09** |
| 2026-01-25 | 0.29 | 0.65 | **0.07** |
| 2026-04-20 | 0.60 | 0.40 | **0.00** |
| 2026-05-25 (8 cells) | 0.18 | 0.83 | **0.00** |

**What this shows:**
- Bare ground at R1 peaked in early 2025 and has mostly been covered since. This fits the original package's explanation that R1 conflicts with WorldCover 2021 because of recent land-use change: clearing, swidden or earthworks.
- Median EMIT NDVI over R1 is 0.43 (2025-01-22) and 0.36 (2026-01-25), and only 5–7 of ~15 EMIT pixels are at or below 0.35.

**Caveat:**
- Kaolinite was still detected on 2026-01-25 while FRCOV gave only 7% bare soil.
- FRCOV unmixing can assign bright, kaolinitic soil partly to the dry-vegetation class.
- So the trend is reliable but the absolute numbers are not.

---

## 5. Candidate points C01–C10

- **Too close together for EMIT:** EMIT pixels are about 60 m across. The candidates are 30–60 m apart, and on several dates two of them fall in the **same EMIT pixel**: C05/C09, C06/C09 and C02/C10. EMIT cannot rank points at this spacing.
- **Persistence across usable dates:**

| ID | Usable dates | Fe-oxide dates | Clay/mica dates | Note |
|---|---|---|---|---|
| C02 | 3 | 3 | 2 | most consistent Fe signal (south slope) |
| C08 | 3 | 3 | 3 | most consistent overall; foot of slope, could be transported material |
| C04 | 3 | 1 | 2 | |
| C05 | 2 | 1 | 2 | |
| C07 | 2 | 1 | 1 | halloysite never repeated |
| C03 | 2 | 0 | 0 | **dickite never repeated; no detection at all on usable dates** |
| C10 | 1 | 1 | 1 | former "Rank 1 / DH-R1-01"; only one usable date |
| C01, C06, C09 | 1 | ≤1 | 1 | |

- **The plan's ranking does not hold up:**
  - C10, C07 and C03 were the three proposed drill collars. Across dates they are among the weakest-supported points.
  - The most consistent Fe-oxide signal is on the south slope (C02, C08). That slope is downhill, so it can collect transported lateritic material.
- **Values that are not in the data:** the Fe band depths that `generate_report_visuals.py` gives C03 (0.020), C04 (0.030) and C09 (0.010) do not appear in any EMIT file.

---

## 6. What should change in the R1 plan

| Item in current plan | Status | Replace with |
|---|---|---|
| "Clear hydrothermal fingerprint", "epithermal system" | ❌ not supported | "Persistent kaolinite + Fe-oxide on exposed soil; consistent with lateritic weathering; hydrothermal origin untested" |
| Dickite at C03, halloysite at C07 as key evidence | ❌ single-pixel, single-date | Remove |
| 10 ranked drill candidates | ❌ below EMIT resolution | Use R1 as **one field-check area**; sample on a grid, not on the 10 points |
| DH-R1-01/02/03 with azimuth/dip | ❌ no structural or geochemical basis | Defer until mapping and assays exist |
| "Inferred NE–SW structural trend" | ❌ no data behind it | Remove, or map structure in the field |
| Pre-drill validation (GNSS → panning → trenching → assay) | ✅ keep | Add an R1 land-use check: who cleared it and when. Add soil and rock-chip SWIR (field spectrometer) and XRD to tell hypogene from supergene clays |

**Field priorities, in order:**
1. **Confirm the location.** Verify the UTM 47N assumption with GNSS.
2. **Find out why R1 is bare.** Determine whether it is cultivation, a road, a quarry or old workings, and photograph it.
3. **Sample.** Map outcrop and float, and take soil samples on a grid of about 25–50 m across R1 and the gullies below C02/C08. Take rock chips wherever quartz veins or gossanous material are found.
4. **Analyse.** Run Au fire assay with multi-element ICP-MS, plus SWIR/XRD on the clays. These are the steps that can confirm or rule out a gold-related system.

---

## 7. Method notes and limitations

- **Data:**
  - EMIT L2B MIN v001 for 8 dates (2025-01-22 and Jan–May 2026).
  - L2A MASK v002 for the same 8 dates.
  - L2B FRCOV v001 for 7 dates.
  - L2A RFL for 2 dates (NDVI and the bare-ground control).
- **R1 overlap rule:** an EMIT pixel counts as part of R1 if its centre is within 30 m of an R1 20 m cell centre. This gives 14–18 EMIT pixels per date. Each candidate is matched to the nearest EMIT pixel within 45 m.
- **Classifier limits:** L2B MIN comes from EMIT's Tetracorder-based dust-source product. Its library matches are best-fit labels, not validated identifications; perchlorate and witherite on hazy dates show how matches degrade. Band depth is not abundance.
- **Small samples:** usable pixel counts at R1 are small (16 and 5 on the clean dates), so the percentages in §3 carry large uncertainty.
- **Bare-ground control:** it uses EMIT NDVI from only the two dates with local reflectance.
