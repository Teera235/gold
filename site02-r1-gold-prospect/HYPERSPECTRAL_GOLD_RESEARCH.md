# Hyperspectral Remote Sensing for Gold Potential: What It Can and Cannot Tell Us

*Research note for the Sangthong (Vientiane, Lao PDR) screening project. Compiled October 2026. Every important claim has a source link. Anything we could not verify is marked **[unverified]** or left out.*

---

## 0. Summary

1. **Gold has no spectral signature.** Imaging spectroscopy detects only minerals with absorption features in the 0.4–2.5 µm range: iron oxides and sulfates, clays, micas, carbonates and sulfates. A gold call is therefore always an inference from an **alteration assemblage** and its **spatial zonation**, never a direct detection.
2. **The minerals EMIT reported in patch R1 are the most common products of tropical weathering.** Goethite, jarosite, kaolinite, halloysite and Fe oxyhydroxides form routinely through lateritic weathering and supergene oxidation of pyrite. Dickite is the only phase on the list that leans toward a hydrothermal origin, and a single dickite match from a 60 m pixel is weak evidence.
3. **EMIT L2B was built for dust-source mineralogy in arid regions.** Its own documentation says that minerals outside the "EMIT-10" set need further validation, particularly for resource exploration. Its validation sites are all desert sites in the SW USA.
4. **A 4 ha bare patch inside ~96% tree cover covers only about 11 EMIT pixel areas**, and most of those pixels are mixed with vegetation. "Dry grass" matches in the same patch confirm that non-photosynthetic vegetation is in the signal.
5. **R1 is a reason to visit the site, not a drill target.** The steps that must come before any drill-hole claim are field spectroscopy, XRD, mapping, rock-chip and soil geochemistry, and geophysics (Section 7).

---

## 1. Physical basis: what the spectra actually measure

Reflectance features in the visible to short-wave infrared (VNIR–SWIR) come from two sources ([Hunt 1977](https://doi.org/10.1190/1.1440721)):

- **Electronic processes** in transition metals (crystal-field and charge-transfer bands), mainly Fe²⁺ and Fe³⁺, in the 0.4–1.3 µm range.
- **Vibrational overtones and combinations** of OH, H₂O and CO₃ in the 1.3–2.5 µm range.

EMIT's Tetracorder setup reflects this split. "Group 1" holds electronic absorptions in the visible and 1 µm regions, and "Group 2" holds narrow absorptions in the 2–2.5 µm region (clays, carbonates, sulfates) ([EMIT L2B ATBD v1.0, 2023, Table 2](https://lpdaac.usgs.gov/documents/1659/EMITL2B_ATBD_v1.pdf)).

### 1.1 Diagnostic features

| Feature / mineral | Approximate position | Notes | Source |
|---|---|---|---|
| Fe³⁺ oxides and hydroxides (goethite, hematite, jarosite) | Crystal-field bands near 0.485, 0.66 and **~0.9 µm** | Band shape and position separate goethite, hematite and jarosite. Grain size changes band saturation. | [Rockwell 2004, USGS OFR 2004-1431](https://pubs.usgs.gov/of/2004/1431/OF04-1431_v12.pdf) |
| Fe²⁺ (chlorite, pyroxene, olivine, Fe-carbonate) | Broad ~1 µm region | EMIT Group 1 "1-micron region" | [Hunt 1977](https://doi.org/10.1190/1.1440721); [EMIT L2B ATBD](https://lpdaac.usgs.gov/documents/1659/EMITL2B_ATBD_v1.pdf) |
| Al-OH (kaolinite, alunite, pyrophyllite, illite, muscovite) | **~2.17–2.21 µm** | A single feature near 2.2 µm can come from many minerals | [Sun et al. 2017, Geoscience Frontiers](https://doi.org/10.1016/j.gsf.2016.10.008) |
| Fe-OH (chlorite, nontronite, jarosite) | ~2.21–2.30 µm | | [Sun et al. 2017](https://doi.org/10.1016/j.gsf.2016.10.008) |
| Mg-OH (chlorite, talc, epidote-group) and carbonate CO₃ | Mg-OH ~2.30–2.40 µm; CO₃ ~2.32–2.35 µm | Chlorite Mg-OH and carbonate overlap near 2.33–2.35 µm | [Sun et al. 2017](https://doi.org/10.1016/j.gsf.2016.10.008); [Yechangping SWIR study, OGR 2025](https://www.sciencedirect.com/science/article/pii/S0169136825004330) |
| **White mica Al-OH position (Pos2200)** | ~2190 nm (Na-rich, paragonitic) → ~2200 nm (muscovite) → ~2210–2225 nm (phengitic) | Shift is driven mainly by Tschermak substitution. Used as a vector to fluid chemistry and temperature, but the direction toward ore depends on the deposit. | [Duke 1994, Geology 22](https://webpages.sdsmt.edu/~eduke/Publications.html); [Wang et al. 2017, Sunrise Dam & Kanowna Belle](https://www.researchgate.net/publication/317098741_White_Mica_as_a_Hyperspectral_Tool_in_Exploration_for_the_Sunrise_Dam_and_Kanowna_Belle_Gold_Deposits_Western_Australia); [Xiaonangou study, OGR 2024](https://www.sciencedirect.com/science/article/pii/S0169136824004827) |
| **Kaolinite** | Doublets at ~1395/1412 nm and **~2160/2208 nm** | In well-ordered kaolinite both doublet members are distinct. In poorly ordered kaolinite the short member is only a shoulder. | [Spectral Evolution app note](https://spectralevolution.com/application-notes-minerals/distinguish-kaolinite-from-halloysite/) |
| **Dickite** | Doublet; short-wavelength member ~8 nm offset from kaolinite near 2165 nm; OH doublet near 1380 nm | Needs high spectral resolution. Multispectral sensors cannot separate dickite from kaolinite. | [EarthDaily/EnMAP Cuprite comparison](https://earthdaily.com/blog/improvements-mineralogical-classification-comparing-fused-bare-earth-composite-enmap-data); [Spectral Evolution dickite note](https://spectralevolution.com/application-notes-minerals/identifying-dickite-with-a-field-spectrometer/) |
| **Halloysite** | Kaolinite-like (poorly ordered) doublet plus a strong, broad H₂O band at ~1912 nm | Separating it from kaolinite in the lab may need intercalation tests, not SWIR alone | [Spectral Evolution](https://spectralevolution.com/application-notes-minerals/distinguish-kaolinite-from-halloysite/); [Kyne et al. 2013](https://doi.org/10.2113/econgeo.108.5.1147) |
| **Alunite** | OH doublet ~1.43/1.48 µm; ~1.76 µm; strong ~2.17 µm; weaker ~2.32 µm | The 1.76 µm band is a key discriminator from kaolinite and pyrophyllite | [Detection of jarosite and alunite with hyperspectral imaging (Mars-analogue study)](https://www.researchgate.net/publication/252891864_Detection_of_Jarosite_and_Alunite_with_Hyperspectral_Imaging_Prospects_for_Determining_Their_Origin_on_Mars_Using_Orbital_Sensors); [LPSC 2019 alunite–kaolinite mixtures](https://www.hou.usra.edu/meetings/lpsc2019/pdf/2576.pdf) |
| **Pyrophyllite** | Sharp, symmetric ~2.165–2.166 µm with a small shoulder near 2.195 µm; OH ~1.395 µm | Overlaps with alunite and kaolinite near 2.165 µm | [Burin Peninsula AA study](https://www.researchgate.net/publication/399149128_Advanced_argillic_alteration_zones_of_the_Burin_Peninsula_Newfoundland_new_insights_utilizing_field-based_shortwave_infrared_spectrometry); [Yerington hyperspectral study](https://www.academia.edu/89001566/Using_hyperspectral_imagery_for_identification_of_pyrophyllite_muscovite_intergrowths_and_alunite_in_the_shallow_epithermal_environment_of_the_Yerington_porphyry_copper_district) |
| **Jarosite** | Fe³⁺ bands in VNIR plus Fe-OH ~2.26 µm | Common product of pyrite oxidation | [Rockwell 2004](https://pubs.usgs.gov/of/2004/1431/OF04-1431_v12.pdf); [ASTER alunite/jarosite study, OGR 2016](https://www.sciencedirect.com/science/article/abs/pii/S0169136816300063) |
| Dry vegetation (cellulose, lignin) | ~2.1 µm (cellulose), ~2.3 µm (lignin) | Most soils lack the 2.1 µm band and instead show clay Al-OH at 2.2 µm. Mixed soil–litter pixels blur this. | [Nagler et al. 2000, RSE](https://www.sciencedirect.com/science/article/abs/pii/S0034425799000826); [Cellulose Absorption Index study, RSE 2003](https://www.sciencedirect.com/science/article/abs/pii/S0034425703001883) |

Exact band centres vary by a few nm between sources and instruments. Treat the numbers above as guides, not thresholds.

### 1.2 Practical consequences

- **Kaolinite, dickite and halloysite are separated by subtle doublet shape and water-band differences.** Hydrothermal dickite can be separated from weathering kaolinite by the shape and crystallinity of the 2.16/2.20 µm doublet, but not at multispectral (e.g., ASTER) resolution ([Minerals 2020 preprint](https://sciforum.net/manuscripts/9353/manuscript.pdf)). At 60 m with mixed pixels, expect these calls to be noisy.
- **No published SWIR crystallinity threshold cleanly separates hypogene from supergene kaolinite.** Many kaolin bodies have mixed origins, and the reliable discriminators are mineral associations, isotopes and field context ([Kyne et al. 2013](https://doi.org/10.2113/econgeo.108.5.1147); [hydrothermal kaolin review, Minerals 2024](https://www.mdpi.com/2075-163X/14/4/353)).

---

## 2. Alteration models for gold deposit types

### 2.1 Assemblages by deposit type

| Deposit type | Diagnostic assemblage / zonation (what to look for) | Key refs |
|---|---|---|
| **High-sulphidation (HS) epithermal** | Advanced argillic core: vuggy silica → quartz–alunite → pyrophyllite/dickite/kaolinite, grading outward to argillic and propylitic. Fluids are acidic and magmatic-derived. **Zonation** around a structural or lithological feeder matters more than any single mineral. | [Hedenquist, Arribas & Gonzalez-Urien 2000](https://doi.org/10.5382/Rev.13.07); [Arribas HS characteristics](https://www.researchgate.net/publication/268376300_Characteristics_of_high-sulfidation_epithermal_deposits_and_their_relation_to_magmatic_fluid) |
| **Low-sulphidation (LS) epithermal** | Proximal adularia–quartz–illite → illite–smectite → distal chlorite–epidote–calcite–albite. Often capped by a **steam-heated kaolinite–alunite–opal blanket above the palaeo-water table, which is typically barren** (no metal anomaly except Hg). | [Alkaline-hosted epithermal alteration study, OGR 2017](https://www.sciencedirect.com/science/article/pii/S0169136817302913); [Hedenquist & Arribas 2022](https://doi.org/10.5382/econgeo.4880) |
| **Porphyry Cu–Au** | Potassic core → phyllic (sericite/white mica) → propylitic (chlorite–epidote–carbonate). An overlying advanced argillic **lithocap** may contain pyrophyllite, alunite and dickite. Many lithocaps are barren. | [Sillitoe 2010, Econ. Geol. 105](https://doi.org/10.2113/gsecongeo.105.1.3); [lithocap "discovery vs dogma"](https://www.researchgate.net/publication/356602963_Lithocap_alteration_epithermal_gold_mineralization_or_not_and_the_transition_to_the_tops_of_porphyry_deposits_Discovery_vs_dogma) |
| **Orogenic gold** | Carbonate (ankerite, Fe-dolomite, calcite), sericite/white mica, chlorite ± albite, and disseminated pyrite/arsenopyrite in shear zones. White-mica Pos2200 and chlorite chemistry are the useful SWIR vectors. | [Groves et al. 1998, OGR 13](https://pubs.usgs.gov/publication/70021148); [USGS low-sulfide quartz-gold model](https://pubs.usgs.gov/of/2003/of03-077/text.htm); [Wang et al. 2017](https://www.researchgate.net/publication/317098741_White_Mica_as_a_Hyperspectral_Tool_in_Exploration_for_the_Sunrise_Dam_and_Kanowna_Belle_Gold_Deposits_Western_Australia) |
| **Carlin-type** | Decarbonatization, argillization (kaolinite, dickite, fine illite) and jasperoid silicification in carbonate host rocks. Alteration correlates **poorly** with gold grade. | [Cline et al. 2005](https://pyrite.utah.edu/fieldtrips/SEGFnevada2007/Readings/General_CTD/Cline2005.pdf) |

### 2.2 Minerals that do *not* indicate hydrothermal activity on their own

Hedenquist & Arribas (2022) list five settings in which advanced argillic minerals form. One of them is **supergene**: weathering and oxidation of pyrite generates H₂SO₄ in the vadose zone and forms **kaolinite, alunite and Fe oxyhydroxides**. They also warn that kaolinite from one setting is easily misattributed to another ([Hedenquist & Arribas 2022, Econ. Geol. 117:609–643](https://doi.org/10.5382/econgeo.4880)).

| Mineral | Why it is non-diagnostic in tropical terrain |
|---|---|
| **Kaolinite** | A standard end-product of weathering of nearly all rocks, along with hematite, goethite and gibbsite ([Anand 2002, regolith geology of the Yilgarn](https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1440-0952.2002.00912.x)). Thick tropical profiles are kaolinite- and goethite-rich ([Goa laterite study](https://www.researchgate.net/publication/42800308_Evolution_of_Laterite_in_Goa)). |
| **Goethite / hematite** | Dominant ferruginous phases of lateritic duricrust and the mottled zone (same sources). In a laterite they say nothing about hydrothermal activity. |
| **Halloysite** | Usually read as supergene. At Cerro la Mina (Mexico), XRD + SWIR showed halloysite with **gypsum and jarosite is supergene**, while halloysite with quartz, alunite, dickite, kaolinite and pyrite was interpreted as hypogene ([Kyne et al. 2013, Econ. Geol. 108](https://doi.org/10.2113/econgeo.108.5.1147); association summary in [Minerals 2024 review](https://www.mdpi.com/2075-163X/14/4/353)). |
| **Jarosite** | Forms by supergene, subaerial weathering of pyrite. Goethite progressively replaces it as the pyrite is used up, which gives jarosite → jarosite+goethite → goethite zonation around oxidising pyrite. Supergene kaolinite and gypsum form at the same time ([Rockwell 2004](https://pubs.usgs.gov/of/2004/1431/OF04-1431_v12.pdf)). Jarosite also forms in **acid sulfate soils** ([remote sensing of acid sulfate soils](https://www.osti.gov/etdeweb/biblio/20061814)). It therefore indicates that pyrite is or was present, not how the pyrite got there. Disturbed ground with exposed sulfide (mine spoil, road cuts) produces the same signal. |

Jarosite does carry some information, because it implies a sulfide source. But pyrite is common in barren sediments, propylitic rocks and black shales, so jarosite is not a gold indicator by itself.

---

## 3. Sensors

| Sensor | Platform | Spectral | Spatial | SWIR SNR (as reported) | Status / notes |
|---|---|---|---|---|---|
| **EMIT** | ISS | 285 bands, 381–2493 nm, ~7.5 nm | **60 m** (nominal at equator); swath ~72 km per [user guide](https://lpdaac.usgs.gov/documents/1660/EMITL2BMIN_User_Guide_V1.pdf) (other sources quote 75–80 km) | >500 at 700 nm (on-orbit, as cited from Thompson et al. 2024). Noise allows "percent-level discrimination" of absorption depths. | Operating since July 2022 ([Thompson et al. 2024, RSE 303:113986](https://doi.org/10.1016/j.rse.2023.113986); [NASA Earthdata](https://www.earthdata.nasa.gov/news/feature-articles/meet-emit-newest-imaging-spectrometer)) |
| **AVIRIS-NG** | Airborne | 380–2510 nm, 5 nm | ~0.3–4 m from low altitude, up to ~20 m from higher altitude | High | [JPL](https://www.jpl.nasa.gov/missions/airborne-visible-infrared-imaging-spectrometer-next-generation-aviris-ng/); [ORNL DAAC](https://daac.ornl.gov/AVIRIS/guides/AVIRIS-NG_L2_Reflectance.html) |
| **AVIRIS (classic)** | Airborne | 224 bands, 0.4–2.5 µm | Altitude-dependent | ~500:1 SWIR (high-altitude, per Kruse) | Reference instrument for Tetracorder/Cuprite work ([Kruse, NASA report](https://ntrs.nasa.gov/api/citations/20050192448/downloads/20050192448.pdf); [Swayze et al. 2014](https://doi.org/10.2113/econgeo.109.5.1179)) |
| **Hyperion** (EO-1) | Satellite | 242 bands, 0.4–2.5 µm, ~10 nm | 30 m | ~50:1 SWIR | Archive only. Gives basic mineralogy similar to AVIRIS but loses fine spectral detail ([Kruse et al. 2003](https://ieeexplore.ieee.org/document/1220247/)) |
| **PRISMA** | Satellite | ~12 nm | 30 m | ~100 at 1.95–2.35 µm | [eoPortal](https://www.eoportal.org/satellite-missions/prisma-hyperspectral) |
| **EnMAP** | Satellite | 6.5 nm VNIR / 10 nm SWIR | 30 m, 30 km swath | >170 at 2200 nm | [EnMAP science review, RSE 2024](https://www.sciencedirect.com/science/article/pii/S003442572400405X) |
| **HyMap** | Airborne | 126 bands, 0.45–2.5 µm, ~15 nm | 3–10 m | 500–1000+ | Commercial exploration workhorse ([Cocks et al. 1998](https://www.ugpti.org/smartse/research/citations/downloads/Cocks-HyMAP-1998.pdf)) |
| **ASTER** | Satellite | 6 SWIR bands | 30 m | n/a | **SWIR unusable since April 2008**. Archive before then only. Cannot separate dickite from kaolinite. ([LP DAAC advisory](https://lpdaac.usgs.gov/documents/1661/ASTER_SWIR_User_Advisory_Jan_12_2009.pdf); [AST_L1T guide](https://lpdaac.usgs.gov/documents/647/AST__L1T_User_Guide_V3.pdf)) |
| **WorldView-3** | Satellite | 8 SWIR bands | 3.7 m native; historically delivered at 7.5 m | n/a | Maps dominant alunite, kaolinite, muscovite etc. at Cuprite ([Kruse, Baugh & Perry 2015](https://www.spiedigitallibrary.org/JournalArticle/Download?urlId=10.1117%2F1.JRS.9.096044); [eoPortal](https://www.eoportal.org/satellite-missions/worldview-3); [Apollo Mapping](https://apollomapping.com/blog/worldview-3-swir-update-3-7-meter-resolution-updated-pricing)) |
| **Sentinel-2 MSI** | Satellite | Only B11 (~1610 nm) and B12 (~2190 nm) in SWIR | 20 m | n/a | Can flag "clay/OH present" broadly. **Cannot** identify specific clays. ([ESA Sentinel-2 resolutions](https://sentinel.esa.int/en/web/sentinel/user-guides/sentinel-2-msi/resolutions/spatial)) |

**For this project:** EMIT's spectral quality is good. Its weakness here is **spatial**: 60 m pixels over small, vegetated exposures. EnMAP or PRISMA (30 m) or WorldView-3 SWIR (3.7 m) are the natural next satellite checks on R1. An airborne survey (HyMap or AVIRIS-class) would be the step after that if field results justify it.

### 3.1 What the EMIT L2B mineral product is, and what it is not

Facts from the [EMIT L2B ATBD v1.0 (May 2023)](https://lpdaac.usgs.gov/documents/1659/EMITL2B_ATBD_v1.pdf) and [L2BMIN User Guide](https://lpdaac.usgs.gov/documents/1660/EMITL2BMIN_User_Guide_V1.pdf):

- **Purpose.** The product exists to constrain mineral-dust radiative forcing. The user guide describes EMIT as measuring the surface mineralogy "of the Earth's arid dust source regions".
- **EMIT-10.** Ten minerals are "the core focus": calcite, chlorite, dolomite, goethite, gypsum, hematite, illite+muscovite, kaolinite, montmorillonite and vermiculite. Note that **jarosite, halloysite and dickite are not among them.**
- **Disclaimer (verbatim).** "Additional minerals are included in the L2BMIN product for transparency and completeness, but were not the focus of this effort. **Further validation is required to use these additional mineral maps – particular in the case of resource exploration.**" The ATBD also notes that separating minerals with similar spectral features, such as fine-grained goethite versus hematite, "is an area of active research".
- **Algorithm.** Tetracorder 5.27. For each pixel, the spectrum is continuum-removed over predefined features and least-squares fitted to library spectra (USGS splib06 plus a research library). The best fit in each spectral group is reported as the "observed" material, together with band depth and a fit score (R²). Matches must pass thresholds on fit, depth, brightness and continuum slope.
- **One answer per group per pixel.** Only the single best Group 1 match and the single best Group 2 match are delivered. Many library entries are **mixtures**, for example "Kaol.5+Musc", "Goeth+qtz.5+Jarosite.5" and "Grass_dry+0.17%Na-Mont". Several Group 2 entries are **vegetation or man-made materials** (dry long grass, golden dry grass, plywood) ([EMIT mineral grouping matrix](https://github.com/emit-sds/emit-sds-l2b/blob/develop/data/mineral_grouping_matrix_20230503.csv)). A "kaolinite+muscovite" label means "best fit to a library mixture", not "both minerals confirmed".
- **Uncertainty.** The reported band-depth uncertainty propagates reflectance noise only. The ATBD states that "misidentification of minerals within the spectral library … would not be captured", and that the fit score "does not fully capture misidentification".
- **Validation.** Validation was done at **desert sites in the SW USA** (Cuprite, Arches, Mountain Pass, Salton Sea, White Sands). No validation in humid tropical terrain is documented.
- **Vegetation handling downstream.** EMIT's own L3 aggregation discards pixels where the soil fraction is below **0.65**. It also masks anthropogenic land use "as our endmember libraries are optimized for natural desert areas" ([EMIT L3 ATBD v3, Jul 2025](https://lpdaac.usgs.gov/documents/2259/EMIT_L3_ATBD_V3.pdf)). The L2B per-pixel IDs carry no such mask, so it is up to the user to apply one.
- **Software note.** A bug in the separate `tetracorder-lite` package mislabelled some Group 2 IDs, including K-jarosite. It was reported as not affecting the operational L2B aggregator ([issue #17](https://github.com/emit-sds/tetracorder-lite/issues/17)). This only matters if the team re-ran Tetracorder with that package.

**Exploration use of EMIT is new.** Published and conference examples are all from **arid** terrain: Yerington lithocap chemistry ([Portela, GRSG 2025 abstract](https://www.grsg.org.uk/abstract-2025-bruno-portela); [Ore Geol. Rev. 2025](https://www.sciencedirect.com/science/article/pii/S0169136825002331)) and EMIT+PRISMA in central Iran ([2026 study](https://www.sciencedirect.com/science/article/pii/S2590056026000083)). We found no published EMIT exploration case in a humid tropical forest.

---

## 4. Methods

| Method | What it does | Strengths / caveats |
|---|---|---|
| **Continuum removal + band depth** | Divides the spectrum by a hull or straight line across a feature, then measures depth and position | Foundation of Tetracorder and wavelength mapping (EMIT ATBD Eqs 1–5). Position mapping (e.g., Pos2200) needs good SNR and spectral resolution. |
| **Tetracorder** (expert system) | Feature-by-feature least-squares fit against a library, with rule-based thresholds | Transparent, physically based ([Clark et al. 2003, JGR 108(E12)](https://doi.org/10.1029/2002JE001847)). It is only as good as its library: materials missing from the library get the nearest wrong label. |
| **SAM** (spectral angle mapper) | Angle between pixel and reference spectra | Insensitive to illumination. Introduced in the SIPS software ([Kruse et al. 1993, RSE 44](https://doi.org/10.1016/0034-4257(93)90013-N)). Does not handle mixtures. |
| **MTMF** (mixture-tuned matched filtering) | Partial unmixing: target abundance plus an "infeasibility" score | Good for sub-pixel targets ([Boardman & Kruse 2011, IEEE TGRS 49](https://doi.org/10.1109/TGRS.2011.2161585)). False positives are common without careful thresholds. |
| **Linear unmixing / vegetation suppression** | Models a pixel as soil + green vegetation + NPV + minerals | Used in the Bau (Borneo) Hyperion work ([Pour & Hashim 2014](https://www.researchgate.net/publication/260533696_Alteration_mineral_mapping_using_ETM_and_hyperion_remote_sensing_data_at_Bau_Gold_Field_Sarawak_Malaysia)) and in a recent vegetated-terrain GF-5B study ([Minerals 2026](https://www.mdpi.com/2075-163X/16/7/669)) |
| **ML / deep learning** | RF, SVM, CNNs, transformers on spectra or spectral-spatial patches | Strong when trained on **ground truth from the same terrain**. Without that, it reproduces label noise ([Hajaj et al. 2024 review](https://www.sciencedirect.com/science/article/abs/pii/S235293852400082X)). |
| **Data fusion** | Combines hyperspectral data with multispectral, SAR, DEM or geophysics | Standard practice in vegetated terrain (e.g., ETM+ + Hyperion + PALSAR at Bau: [Pour, Hashim & van Genderen 2013, OGR 54](https://www.sciencedirect.com/science/article/abs/pii/S0169136813001066)) |

### 4.1 Validation practice

- **Field or hand-sample SWIR** (ASD/TerraSpec-class spectrometers) on rock chips, outcrop and drill core is the standard way to confirm remote alteration maps and to measure white-mica Pos2200 and kaolinite crystallinity ([Thompson, Hauff & Robitaille 1999, SEG Newsletter 39](https://doi.org/10.5382/SEGnews.1999-39.fea); [Hauff, field spectroscopy overview](https://www.researchgate.net/publication/265275552_An_overview_of_VIS-NIR-SWIR_field_spectroscopy_as_applied_to_precious_metals_exploration)).
- **XRD** and petrography/SEM confirm the mineralogy. Tetracorder's original validation used XRD, electron microprobe, SEM and petrography ([EMIT L2B ATBD §6.2](https://lpdaac.usgs.gov/documents/1659/EMITL2B_ATBD_v1.pdf)).
- **Halloysite versus kaolinite** may need intercalation tests such as formamide ([Kyne et al. 2013](https://doi.org/10.2113/econgeo.108.5.1147)).
- **Hypogene versus supergene kaolin** is best settled by O–H stable isotopes and mineral associations ([hydrothermal kaolin review](https://www.mdpi.com/2075-163X/14/4/353)).
- **Field spectrometers in lateritic saprolite** have trouble identifying phyllosilicates inherited from hypogene alteration because bands overlap ([same review](https://www.mdpi.com/2075-163X/14/4/353)). Sampling fresher material (below the saprolite, in stream beds, in road cuts) helps.

---

## 5. Limitations in tropical, vegetated terrain

1. **Vegetation masks the surface.** As little as ~10% green cover is often cited as able to obscure mineral features ([Siegal & Goetz 1977](https://doi.org/10.1016/0031-8663(77)90007-2) **[secondary citation; original not read]**). In one field study, clays were detectable only where the soil fraction was about **20–30% (mixed with dry vegetation) or 40–50% (mixed with green vegetation)** ([Chabrillat et al. 2002, RSE 82](https://doi.org/10.1016/S0034-4257(02)00060-3); single study, indicative only). EMIT's own L3 requires a soil fraction ≥0.65 ([L3 ATBD](https://lpdaac.usgs.gov/documents/2259/EMIT_L3_ATBD_V3.pdf)). At ~96% regional tree cover (median NDVI ~0.8), almost no EMIT pixels in the box meet any of these thresholds.
2. **Dry vegetation looks like clay.** Cellulose and lignin absorb near 2.1 and 2.3 µm, close to Al-OH (2.2) and Mg-OH/carbonate (2.3) ([Nagler et al. 2000](https://www.sciencedirect.com/science/article/abs/pii/S0034425799000826)). Tetracorder's Group 2 library includes dry-grass and dry-grass+clay mixture spectra. A "dry grass" match next to "kaolinite" matches in the same small patch is a warning that NPV is affecting the 2 µm group.
3. **The regolith blanket.** Deep lateritic weathering replaces primary and hydrothermal minerals with kaolinite, goethite, hematite and gibbsite ([Anand 2002](https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1440-0952.2002.00912.x)). Remote sensing sees the top millimetres of this profile. The surface signal is weathering mineralogy unless erosion exposes fresh rock.
4. **Mixed pixels at 30–60 m.** A 4 ha patch is about 11 EMIT pixel areas (60 × 60 m = 0.36 ha). Because pixel footprints are not aligned to the patch, only a few pixels, if any, are likely to be mostly bare. Finer pixels give purer endmembers in heterogeneous areas ([Chabrillat et al. 2002](https://doi.org/10.1016/S0034-4257(02)00060-3)).
5. **Cloud, haze, terrain illumination and moisture.** Persistent cloud limits clean acquisitions. Shading on steep slopes and wet soils weaken features. EMIT L3 masks AOD > 0.5 as well as cloud, cirrus, water and shade ([L3 ATBD](https://lpdaac.usgs.gov/documents/2259/EMIT_L3_ATBD_V3.pdf)).
6. **Anthropogenic exposures.** Bare patches in forest are often clearings, farms, roads, quarries or mine workings. Fresh cuts through pyritic rock produce jarosite and goethite by oxidation ([Rockwell 2004](https://pubs.usgs.gov/of/2004/1431/OF04-1431_v12.pdf)). EMIT's L3 explicitly masks anthropogenic land use.

### 5.1 Tropical case studies

- **Bau gold field, Sarawak (Borneo).** Tropical climate, limited outcrop, gold described as Carlin-style. Pour and colleagues used Landsat ETM+ (directed PCA of band ratios to suppress vegetation) and Hyperion (linear unmixing) and report that known prospects were "recognizable" despite the cover ([Pour & Hashim 2014, IOP EES 18:012149](https://www.researchgate.net/publication/260533696_Alteration_mineral_mapping_using_ETM_and_hyperion_remote_sensing_data_at_Bau_Gold_Field_Sarawak_Malaysia); [Pour, Hashim & van Genderen 2013](https://www.sciencedirect.com/science/article/abs/pii/S0169136813001066)). This is a **known-deposit retrospective**, not a blind discovery.
- **Bentong–Raub suture, Peninsular Malaysia.** PALSAR (L-band SAR) used for structural mapping of orogenic and sediment-hosted gold systems under forest ([Pour et al. 2016, Resource Geology](https://onlinelibrary.wiley.com/doi/abs/10.1111/rge.12105)).

### 5.2 Regional geology: Laos, Loei and Truong Son

- The **Loei** and **Truong Son** fold belts host the known gold and base-metal deposits of Thailand and Laos. They converge in the Phu Bia district ([PorterGeo](https://portergeo.com.au/database/mineinfo.php?mineid=mn1257); [Tectonics & metallogeny of mainland SE Asia](https://www.researchgate.net/publication/262524876_Tectonics_and_metallogeny_of_mainland_Southeast_Asia_-_A_review_and_contribution)).
- Deposit styles in the region include:
  - **Porphyry Cu–Au:** Phu Kham.
  - **Low-sulphidation epithermal Au–Ag:** Ban Houayxai, in Early Permian arc volcanics ([Manaka et al. 2014, Gondwana Research](https://www.sciencedirect.com/science/article/abs/pii/S1342937X13003080)); Chatree in the Loei belt.
  - **Sediment-hosted Au with Carlin-like features plus Cu skarn:** Sepon ([Sepon thesis, UTas](https://figshare.utas.edu.au/articles/thesis/Geological_setting_geochemistry_and_genesis_of_the_Sepon_gold_and_copper_deposits_Laos/23211731)).
  - **Distal intrusion-related Au in carbonates:** Nam Xan ([Minerals 2026](https://www.mdpi.com/2075-163X/16/6/600)).
- **Sangthong district itself:**
  - The **Sakay** gold deposit is hosted in intermediate volcanic lavas and tuffs along near E–W brittle shear fractures. Ore minerals are pyrite, sphalerite, galena and chalcopyrite. Wall-rock alteration is silicification, carbonatization, sericitization, chloritization and "limonitization". It is interpreted as a low-temperature hydrothermal deposit in a brittle shear zone ([Yang et al. 2025, J. Environ. Earth Sci. 7(5):233–243](https://journals.bilpubgroup.com/index.php/jees/article/view/8514)). Its placement in Sangthong district comes from secondary summaries **[unverified against full text]**.
  - A zircon U–Pb study dates dacite in the "Sangthong Au mining area" of the Luang Prabang–Loei belt ([ResearchGate record](https://www.researchgate.net/publication/384119100_LA-ICP-MS_zircon_U-Pb_dating_of_dacite_in_the_Sangthong_Au_mining_area_Luang_Prabang-Loei_metallogenetic_belt_SW_Laos)).
  - Exploration licences in the district have been reported in news coverage ([example](https://www.funan.com.vn/en/vietnamese-firm-to-explore-for-gold-in-sangthong.121721)).
  - **Implication:** the district is gold-bearing, so an anomaly is geologically plausible. But the *known* local style (shear-hosted, sericite–carbonate–chlorite alteration) does not predict an advanced argillic HS signature. Existing workings near R1 could also explain an oxidised-sulfide surface signal. Check R1 against known mine and concession locations.

---

## 6. Complementary data for forested areas

| Data | What it adds | Note |
|---|---|---|
| **SAR (L-band such as ALOS PALSAR; also C-band Sentinel-1)** | Structure and lineaments through canopy and cloud | Used for gold-system structure in Malaysian rainforest ([Pour et al. 2016](https://onlinelibrary.wiley.com/doi/abs/10.1111/rge.12105)) |
| **DEM (lidar if possible; SRTM/Copernicus 30 m otherwise)** | Lineaments, drainage, landform–regolith mapping, separating colluvium from in-situ material | Lidar sees through canopy to the ground |
| **Airborne magnetics** | Intrusions, magnetite destruction in altered zones, structure | Standard first-pass layer in covered terrain |
| **Airborne radiometrics (K, eTh, eU)** | K enrichment from sericitic/potassic alteration. K/Th ratio highlights alteration. | Potassium is a practical indirect guide to gold-related alteration (Dickson & Scott 1997, AGSO J. 17(2), as summarised in [a citing study](https://www.sciencedirect.com/science/article/abs/pii/S0969804322003967); original not read); [K/eTh in LS epithermal, Türkiye](https://www.researchgate.net/publication/282246599_Gamma_ray_spectrometry_for_recognition_of_hydrothermal_alteration_zones_related_to_a_low_sulfidation_epithermal_gold_mineralization_eastern_Pontides_NE_Turkiye) |
| **Stream-sediment geochemistry (−80# fraction Au + multi-element; BLEG)** | Catchment-scale Au and pathfinder (As, Sb, Hg, Cu, Mo, Te) anomalies, independent of canopy | Batu Hijau (Indonesia) was found from a single BLEG sample of 7.4 ppb Au taken 9 km downstream ([GEEA 2023 stream-sediment review](https://doi.org/10.1144/geochem2022-039)). Fine-fraction total Au can outperform BLEG in tropical surveys ([BRGM arid/tropical comparison](https://www.researchgate.net/publication/242161928_Low_sampling_density_exploration_geochemistry_for_gold_in_arid_and_tropical_climates_Comparison_between_conventional_geochemistry_and_BLEG)). |
| **Soil geochemistry (grid, B-horizon or lag)** | Defines the anomaly footprint at prospect scale | Interpret with regolith mapping, because lateritic profiles redistribute Au and pathfinder elements |
| **IP / resistivity** | Disseminated sulfides and silicification at depth | Reportedly already used for gold in Sangthong ([GeoMine profile](https://anyflip.com/lyank/zriq/basic) **[unverified detail]**) |
| **Geological mapping** | Lithology, structure, alteration, veining, float | Cannot be skipped |

---

## 7. How to apply this to the R1 patch

### 7.1 What the EMIT result does and does not say

**What R1 shows:**
- About 4 ha of exposed ground in otherwise closed forest.
- Group 1 best fit: goethite+jarosite.
- Group 2 best fits, varying between pixels: kaolinite+muscovite, halloysite, dickite, and dry grass.

**Readings consistent with these data:**

| Interpretation | Supported by | Problems |
|---|---|---|
| A. Lateritic or saprolitic soil exposed by clearing, erosion or agriculture | Kaolinite, halloysite and goethite are the standard tropical weathering assemblage. Dry-grass matches indicate a mixed NPV/soil surface. | Does not explain dickite (but see caveats on dickite below) |
| B. Supergene oxidation of pyritic rock, natural or exposed by human activity (road, quarry, workings, spoil) | Jarosite+goethite, kaolinite and halloysite are the typical supergene products of pyrite oxidation ([Rockwell 2004](https://pubs.usgs.gov/of/2004/1431/OF04-1431_v12.pdf); [Hedenquist & Arribas 2022](https://doi.org/10.5382/econgeo.4880)) | Pyrite source unknown. It could be barren. |
| C. Weathered hydrothermal alteration (argillic, advanced argillic or sericitic) | Dickite and white mica fits | Single-pixel, mixed-library, non-EMIT-10 IDs with no ground validation. No alunite, pyrophyllite or vuggy silica reported. No coherent zonation is possible at this size. |

None of these can currently be excluded. Calling R1 a **"confirmed epithermal system" is not supported**:

- **None of the diagnostic HS minerals were reported.** Alunite, pyrophyllite and vuggy silica are missing, and there is no spatial zonation.
- **The detected minerals are explicitly listed as forming supergenely.**
- **The product's authors say non-EMIT-10 minerals need further validation, particularly for resource exploration.**
- **Patch size and vegetation fraction fall below EMIT's own bare-soil threshold** for quantitative use.

### 7.2 Quick desk checks before fieldwork (days)

1. **Pixel audit.** For each R1 pixel, tabulate the Group 1 and Group 2 IDs, band depth, band-depth uncertainty and fit (R²), along with NDVI and the EMIT fractional cover (L2B FRCOV, if available) or an unmixed soil fraction. Flag pixels with soil fraction < 0.65 or a dry-grass ID in a neighbouring pixel.
2. **Repeatability.** Do the same IDs recur in other EMIT acquisitions of R1? One date is weak evidence.
3. **Inspect the reflectance spectra directly.** Look at continuum-removed L2A spectra over 2.1–2.4 µm, and check for a 1.76 µm band (alunite), a sharp 2.165 µm feature (pyrophyllite), the doublet shape (kaolinite vs dickite) and the 1.9 µm water band (halloysite).
4. **Land-use history.** Use time-series Sentinel-2 and Google Earth imagery to find when R1 became bare and what it looks like (road, pit, field, landslide). Cross-check against known mines and concessions (e.g., Sakay).
5. **Independent sensors.** Check EnMAP or PRISMA (30 m) archives, and WorldView-3 SWIR (3.7 m) if budget allows.

### 7.3 Evidence ladder

| Step | Activity | Can establish | Cannot establish |
|---|---|---|---|
| **0. Satellite anomaly** (we are here) | EMIT L2B and L2A, Sentinel-2 | That an exposed surface has Fe³⁺ and Al-OH/kaolin-group spectral character | Origin of the minerals, presence of sulfides, presence of gold, depth extent |
| **1. Desk validation** | Steps in 7.2; higher-resolution imagery; geology maps; DEM/SAR structure | Whether the anomaly is robust, natural or anthropogenic, and structurally sited | Mineral origin |
| **2. Field reconnaissance** | Mapping, photos, outcrop vs soil, veining, boxwork, float; handheld SWIR on 30–100 rock and soil samples | Real mineralogy at the surface; whether alteration minerals sit in rock or only in soil; white-mica Pos2200; presence or absence of alunite, pyrophyllite and dickite | Gold grade; hypogene origin (not yet conclusive) |
| **3. Laboratory confirmation** | XRD, petrography; formamide test for halloysite; O–H isotopes on kaolin if the hypogene/supergene question matters | Hypogene versus supergene origin; true assemblage | Gold endowment |
| **4. Geochemistry** | Rock chips (Au by fire assay + multi-element ICP); soil grid; stream sediments (−80# and/or BLEG) in the catchments draining R1 | Whether Au and pathfinders are anomalous; footprint size; dispersion direction | Grade and continuity at depth |
| **5. Geophysics** | Ground magnetics, IP/resistivity; airborne mag/radiometrics if available | Subsurface sulfide/silica bodies, structure, intrusions | Gold directly |
| **6. Trenching / shallow drilling** (auger or RAB through regolith) | Test the anomaly beneath laterite | Bedrock alteration and Au below the weathering profile | Economic resource |
| **7. Drilling** (RC/diamond) | Test a target defined by steps 2–6 | Grade, width, continuity | Economics, which needs resource drilling and studies |

### 7.4 Minimum evidence before any drill-target claim

A defensible drill target for R1 (or anywhere in the box) should have **at least**:

1. **Field-confirmed alteration in bedrock** (not just soil), identified by handheld SWIR and supported by XRD. The assemblage and zonation must be consistent with a gold deposit model (Section 2), not just kaolinite, goethite and halloysite.
2. **Positive gold geochemistry:** anomalous Au and pathfinder elements in rock chips and/or a coherent soil or stream-sediment anomaly, with a stated background and threshold.
3. **A structural or geological control:** a fault, shear, contact or intrusion mapped in the field or from SAR, DEM or magnetics, that explains where the fluids went.
4. **A geophysical or geochemical target at depth** (e.g., IP chargeability or resistivity feature, magnetic feature) under the surface anomaly.
5. **Legal and practical checks:** tenure and concession status, access, and environmental and community constraints.

Until items 1 and 2 are met, R1 should be reported as **"spectral anomaly – unvalidated; consistent with weathered or supergene material; field check recommended"**.

---

## 8. References

**EMIT documentation and data**
- Brodrick, P.G., Clark, R.N., Swayze, G.A., et al. (2023). *EMIT L2b Algorithm: Mineral Detection and Related Products at the Pixel Scale – Theoretical Basis*, v1.0, JPL D-104479. https://lpdaac.usgs.gov/documents/1659/EMITL2B_ATBD_v1.pdf
- EMIT L2BMIN User Guide (2023), JPL D-107863. https://lpdaac.usgs.gov/documents/1660/EMITL2BMIN_User_Guide_V1.pdf
- Okin, G.S., Ochoa, F., Brodrick, P.G., et al. (2025). *EMIT L3 Algorithm: Aggregated Mineral Mass Fractions*, v3.0, JPL D-104480. https://lpdaac.usgs.gov/documents/2259/EMIT_L3_ATBD_V3.pdf
- EMIT mineral grouping matrix (2023). https://github.com/emit-sds/emit-sds-l2b/blob/develop/data/mineral_grouping_matrix_20230503.csv
- tetracorder-lite issue #17. https://github.com/emit-sds/tetracorder-lite/issues/17
- Thompson, D.R., et al. (2024). On-orbit calibration and performance of the EMIT imaging spectrometer. *Remote Sensing of Environment* 303, 113986. https://doi.org/10.1016/j.rse.2023.113986
- NASA Earthdata, "Meet EMIT". https://www.earthdata.nasa.gov/news/feature-articles/meet-emit-newest-imaging-spectrometer

**Spectroscopy and methods**
- Hunt, G.R. (1977). Spectral signatures of particulate minerals in the visible and near infrared. *Geophysics* 42, 501–513. https://doi.org/10.1190/1.1440721
- Clark, R.N., et al. (2003). Imaging spectroscopy: Earth and planetary remote sensing with the USGS Tetracorder and expert systems. *JGR* 108(E12), 5131. https://doi.org/10.1029/2002JE001847
- Swayze, G.A., et al. (2014). Mapping advanced argillic alteration at Cuprite, Nevada, using imaging spectroscopy. *Economic Geology* 109, 1179–1221. https://doi.org/10.2113/econgeo.109.5.1179
- Rockwell, B.W. (2004). Spectral variations in rocks and soils containing ferric iron hydroxide and(or) sulfate minerals as seen by AVIRIS and laboratory spectroscopy. USGS OFR 2004-1431. https://pubs.usgs.gov/of/2004/1431/OF04-1431_v12.pdf
- Duke, E.F. (1994). Near infrared spectra of muscovite, Tschermak substitution, and metamorphic reaction progress. *Geology* 22, 621–624. (Author page: https://webpages.sdsmt.edu/~eduke/Publications.html)
- Wang, R., et al. (2017). White mica as a hyperspectral tool in exploration for the Sunrise Dam and Kanowna Belle gold deposits. https://www.researchgate.net/publication/317098741
- Xiaonangou white-mica SWIR study (2024), *Ore Geology Reviews*. https://www.sciencedirect.com/science/article/pii/S0169136824004827
- Sun, Y., Tian, S., Di, B. (2017). Extracting mineral alteration information using WorldView-3 data. *Geoscience Frontiers* 8(5), 1051–1062. https://doi.org/10.1016/j.gsf.2016.10.008
- Kruse, F.A., et al. (1993). The Spectral Image Processing System (SIPS). *RSE* 44, 145–163. https://doi.org/10.1016/0034-4257(93)90013-N
- Boardman, J.W., Kruse, F.A. (2011). Analysis of imaging spectrometer data using N-dimensional geometry and a mixture-tuned matched filtering approach. *IEEE TGRS* 49(11), 4138–4152. https://doi.org/10.1109/TGRS.2011.2161585
- Kruse, F.A., et al. (2003). Comparison of airborne hyperspectral data and EO-1 Hyperion for mineral mapping. *IEEE TGRS*. https://ieeexplore.ieee.org/document/1220247/
- Kruse, F.A., Baugh, W.M., Perry, S.L. (2015). Validation of DigitalGlobe WorldView-3 Earth imaging satellite SWIR bands for mineral mapping. *J. Appl. Remote Sens.* 9. https://www.spiedigitallibrary.org/JournalArticle/Download?urlId=10.1117%2F1.JRS.9.096044
- Cocks, T., et al. (1998). The HyMap airborne hyperspectral sensor. https://www.ugpti.org/smartse/research/citations/downloads/Cocks-HyMAP-1998.pdf
- van der Meer, F.D., et al. (2012). Multi- and hyperspectral geologic remote sensing: A review. *Int. J. Appl. Earth Obs. Geoinf.* 14, 112–128. https://doi.org/10.1016/j.jag.2011.08.002
- Bedini, E. (2017). The use of hyperspectral remote sensing for mineral exploration: a review. *J. Hyperspectral Remote Sensing* 7(4), 189–211. https://periodicos.ufpe.br/revistas/jhrs/article/view/25065
- Hajaj, S., El Harti, A., Pour, A.B., et al. (2024). A review on hyperspectral imagery application for lithological mapping and mineral prospecting: machine learning techniques and future prospects. *Remote Sensing Applications: Society and Environment*. https://www.sciencedirect.com/science/article/abs/pii/S235293852400082X
- Thompson, A.J.B., Hauff, P.L., Robitaille, A.J. (1999). Alteration mapping in exploration: application of short-wave infrared (SWIR) spectroscopy. *SEG Newsletter* 39. https://doi.org/10.5382/SEGnews.1999-39.fea
- Hauff, P.L. An overview of VIS-NIR-SWIR field spectroscopy as applied to precious metals exploration. Spectral International Inc. https://www.researchgate.net/publication/265275552
- Spectral Evolution application notes (kaolinite/halloysite; dickite; pyrophyllite). https://spectralevolution.com/application-notes-minerals/distinguish-kaolinite-from-halloysite/ ; https://spectralevolution.com/application-notes-minerals/identifying-dickite-with-a-field-spectrometer/
- EarthDaily (EnMAP vs multispectral at Cuprite). https://earthdaily.com/blog/improvements-mineralogical-classification-comparing-fused-bare-earth-composite-enmap-data

**Vegetation and soil mixing**
- Siegal, B.S., Goetz, A.F.H. (1977). Effect of vegetation on rock and soil type discrimination. *PE&RS* 43, 191–196. https://doi.org/10.1016/0031-8663(77)90007-2
- Chabrillat, S., Goetz, A.F.H., Krosley, L., Olsen, H.W. (2002). Use of hyperspectral images in the identification and mapping of expansive clay soils and the role of spatial resolution. *RSE* 82, 431–445. https://doi.org/10.1016/S0034-4257(02)00060-3
- Nagler, P.L., et al. (2000). Plant litter and soil reflectance. *RSE*. https://www.sciencedirect.com/science/article/abs/pii/S0034425799000826
- Cellulose absorption index (CAI) to quantify mixed soil–plant litter scenes (2003). *RSE*. https://www.sciencedirect.com/science/article/abs/pii/S0034425703001883

**Deposit models and alteration**
- Hedenquist, J.W., Arribas, A., Gonzalez-Urien, E. (2000). Exploration for epithermal gold deposits. *Reviews in Economic Geology* 13, 245–277. https://doi.org/10.5382/Rev.13.07
- Hedenquist, J.W., Arribas, A. (2022). Exploration implications of multiple formation environments of advanced argillic minerals. *Economic Geology* 117(3), 609–643. https://doi.org/10.5382/econgeo.4880
- Sillitoe, R.H. (2010). Porphyry copper systems. *Economic Geology* 105, 3–41. https://doi.org/10.2113/gsecongeo.105.1.3
- Groves, D.I., et al. (1998). Orogenic gold deposits: a proposed classification… *Ore Geology Reviews* 13, 7–27. https://pubs.usgs.gov/publication/70021148
- Cline, J.S., et al. (2005). Carlin-type gold deposits in Nevada: critical geologic characteristics and viable models. *Econ. Geol. 100th Anniversary Vol.* https://pyrite.utah.edu/fieldtrips/SEGFnevada2007/Readings/General_CTD/Cline2005.pdf
- Kyne, R., Hollings, P., Jansen, N.H., Cooke, D.R. (2013). Supergene and hypogene halloysite in a porphyry-epithermal environment at Cerro la Mina, Chiapas, Mexico. *Economic Geology* 108(5), 1147–1161. https://doi.org/10.2113/econgeo.108.5.1147
- Global occurrence, geology and characteristics of hydrothermal-origin kaolin deposits (2024). *Minerals* 14(4), 353. https://www.mdpi.com/2075-163X/14/4/353
- Anand, R.R. (2002). Regolith geology of the Yilgarn Craton, Western Australia: implications for exploration. *Aust. J. Earth Sci.* https://onlinelibrary.wiley.com/doi/abs/10.1046/j.1440-0952.2002.00912.x
- Alkaline-hosted epithermal alteration and fluid pH (2017). *Ore Geology Reviews*. https://www.sciencedirect.com/science/article/pii/S0169136817302913

**Sensors**
- EnMAP initial science results (2024). *RSE*. https://www.sciencedirect.com/science/article/pii/S003442572400405X
- PRISMA – eoPortal. https://www.eoportal.org/satellite-missions/prisma-hyperspectral
- AVIRIS-NG – JPL. https://www.jpl.nasa.gov/missions/airborne-visible-infrared-imaging-spectrometer-next-generation-aviris-ng/
- ASTER SWIR User Advisory (2009). https://lpdaac.usgs.gov/documents/1661/ASTER_SWIR_User_Advisory_Jan_12_2009.pdf
- WorldView-3 – eoPortal. https://www.eoportal.org/satellite-missions/worldview-3
- Sentinel-2 MSI spatial resolutions – ESA. https://sentinel.esa.int/en/web/sentinel/user-guides/sentinel-2-msi/resolutions/spatial

**Tropical / regional case studies**
- Pour, A.B., Hashim, M. (2014). Alteration mineral mapping using ETM+ and Hyperion remote sensing data at Bau Gold Field, Sarawak, Malaysia. *IOP Conf. Ser.: EES* 18, 012149. https://www.researchgate.net/publication/260533696
- Pour, A.B., Hashim, M., van Genderen, J. (2013). Detection of hydrothermal alteration zones in a tropical region using satellite remote sensing data: Bau goldfield. *Ore Geology Reviews* 54, 181–196. https://www.sciencedirect.com/science/article/abs/pii/S0169136813001066
- Pour, A.B., et al. (2016). Structural mapping of the Bentong-Raub suture zone using PALSAR. *Resource Geology*. https://onlinelibrary.wiley.com/doi/abs/10.1111/rge.12105
- Manaka, T., et al. (2014). The Ban Houayxai epithermal Au–Ag deposit, northern Lao PDR. *Gondwana Research*. https://www.sciencedirect.com/science/article/abs/pii/S1342937X13003080
- PorterGeo – Phu Bia / Phu Kham. https://portergeo.com.au/database/mineinfo.php?mineid=mn1257
- Yang, D., Liu, C., et al. (2025). Geological characteristics and preliminary genesis exploration of the Sakay gold deposit in Vientiane, Laos. *J. Environ. Earth Sci.* 7(5), 233–243. https://journals.bilpubgroup.com/index.php/jees/article/view/8514
- Nam Xan gold deposit, Laos (2026). *Minerals* 16(6), 600. https://www.mdpi.com/2075-163X/16/6/600
- Sepon gold and copper deposits, Laos (UTas thesis). https://figshare.utas.edu.au/articles/thesis/Geological_setting_geochemistry_and_genesis_of_the_Sepon_gold_and_copper_deposits_Laos/23211731
- EMIT exploration examples (arid): Portela, GRSG 2025 abstract https://www.grsg.org.uk/abstract-2025-bruno-portela ; *Ore Geol. Rev.* 2025 https://www.sciencedirect.com/science/article/pii/S0169136825002331 ; EMIT+PRISMA, central Iran (2026) https://www.sciencedirect.com/science/article/pii/S2590056026000083

**Complementary methods**
- Stream sediment geochemistry in mineral exploration: a review… (2023). *Geochemistry: Exploration, Environment, Analysis*. https://doi.org/10.1144/geochem2022-039
- Low sampling density exploration geochemistry for gold in arid and tropical climates: conventional geochemistry vs BLEG. https://www.researchgate.net/publication/242161928
- Dickson, B.L., Scott, K.M. (1997). Interpretation of aerial gamma-ray surveys – adding the geochemical factors. *AGSO J. Aust. Geol. Geophys.* 17(2), 187–200. (Cited via secondary sources; original not accessed.)
- Gamma-ray spectrometry for LS epithermal alteration, eastern Pontides. https://www.researchgate.net/publication/282246599
