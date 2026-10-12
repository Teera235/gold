#!/usr/bin/env python3
"""
Generate High-Quality Visualizations for R1 Candidates Report
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Polygon as MplPolygon
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe
from scipy.ndimage import label, gaussian_filter
import rasterio
import h5py
import pyproj

os.makedirs('visuals', exist_ok=True)
base_dir = 'drive-download-20261011T175941Z-1-001/02_Maps'

# 1. Load Rasters
with rasterio.open(f'{base_dir}/historical_cover_disagreement.tif') as ds_dis:
    disagree = ds_dis.read(1)
    tr_dis = ds_dis.transform

with rasterio.open(f'{base_dir}/Map_Sheets/07_Elevation.tif') as ds_elev:
    elev = ds_elev.read(1)
    tr_elev = ds_elev.transform

with rasterio.open(f'{base_dir}/Map_Sheets/08_Slope.tif') as ds_slope:
    slope = ds_slope.read(1)
    tr_slope = ds_slope.transform

# 2. Extract R1 Patch (ID 90, 3.92 ha, 98 pixels)
lbl, _ = label(disagree == 1)
r1_mask = (lbl == 90)
ys, xs = np.where(r1_mask)
r1_eastings = tr_dis.c + xs * tr_dis.a + ys * tr_dis.b
r1_northings = tr_dis.f + xs * tr_dis.d + ys * tr_dis.e

# 3. Candidate Points definition
candidates = [
    {"id": "C10", "e": 779502.0, "n": 2021538.0, "lat": 18.265105, "lon": 101.643454, "elev": 362.5, "slope": 11.3, "rank": 1, "mineral": "Goethite+Qtz+Jarosite (0.100) & Kaolinite+Mica (0.200)", "fe": 0.100, "clay": 0.200, "desc": "ศูนย์กลางแร่น้ำร้อนและหมวกเหล็กเข้มข้นสูงสุด (เป้าหลักหลุมเจาะ DH-R1-01)"},
    {"id": "C07", "e": 779535.5, "n": 2021584.5, "lat": 18.265521, "lon": 101.643776, "elev": 396.4, "slope": 24.5, "rank": 1, "mineral": "Halloysite (0.159) & Goethite+Jarosite (0.078)", "fe": 0.078, "clay": 0.159, "desc": "รอยแตกโครงสร้างสันเขา พบแร่ Halloysite หนาแน่น (เป้าเจาะ DH-R1-02)"},
    {"id": "C06", "e": 779435.5, "n": 2021566.4, "lat": 18.265370, "lon": 101.642829, "elev": 366.6, "slope": 16.5, "rank": 1, "mineral": "Kaolinite+Muscovite (0.135) & Goethite (0.084)", "fe": 0.084, "clay": 0.135, "desc": "ไหล่เขาด้านตะวันตก โซนแปรสภาพ Phyllic Alteration สมบูรณ์"},
    {"id": "C02", "e": 779548.0, "n": 2021496.0, "lat": 18.264720, "lon": 101.643883, "elev": 359.6, "slope": 9.5, "rank": 2, "mineral": "Kaolinite+Muscovite (0.133) & Goethite (0.090)", "fe": 0.090, "clay": 0.133, "desc": "ทางลาดด้านใต้ ลานเปิดโล่งความชันต่ำ เหมาะตั้งแท่นเจาะ"},
    {"id": "C01", "e": 779467.5, "n": 2021615.0, "lat": 18.265805, "lon": 101.643138, "elev": 372.2, "slope": 18.7, "rank": 2, "mineral": "Kaolinite+Muscovite (0.120) & Goethite (0.076)", "fe": 0.076, "clay": 0.120, "desc": "สันเขาด้านตะวันตกเฉียงเหนือ แนวต่อเชื่อมโครงสร้าง"},
    {"id": "C03", "e": 779522.9, "n": 2021664.3, "lat": 18.266243, "lon": 101.643668, "elev": 384.2, "slope": 4.7, "rank": 2, "mineral": "Dickite (0.059) Advanced Argillic indicator", "fe": 0.020, "clay": 0.059, "desc": "ลานกว้างบนยอดเนิน ชันเพียง 4.7° พบ Dickite ชี้วัดระบบ Epithermal อุณหภูมิสูง"},
    {"id": "C04", "e": 779588.6, "n": 2021617.1, "lat": 18.265809, "lon": 101.644283, "elev": 403.5, "slope": 14.5, "rank": 3, "mineral": "Kaolinite+Muscovite (0.088)", "fe": 0.030, "clay": 0.088, "desc": "ยอดเนินเขาสูงสุดของแปลง R1 (403.5 ม.) ขอบด้านตะวันออก"},
    {"id": "C08", "e": 779607.1, "n": 2021464.3, "lat": 18.264426, "lon": 101.644437, "elev": 356.4, "slope": 22.7, "rank": 3, "mineral": "Goethite+Jarosite (0.071) & Kaolinite (0.086)", "fe": 0.071, "clay": 0.086, "desc": "ร่องน้ำเชิงเขาทิศใต้ จุดรวมตะกอนชะล้างจากแกนกลางแร่"},
    {"id": "C05", "e": 779330.0, "n": 2021540.0, "lat": 18.265146, "lon": 101.641828, "elev": 368.6, "slope": 12.6, "rank": 3, "mineral": "Kaolinite+Muscovite (0.082)", "fe": 0.004, "clay": 0.082, "desc": "ขอบสุดด้านตะวันตกของแปลง R1 รอยต่อแนวป่า"},
    {"id": "C09", "e": 779374.4, "n": 2021583.3, "lat": 18.265531, "lon": 101.642254, "elev": 372.2, "slope": 19.5, "rank": 3, "mineral": "Kaolinite+Muscovite (0.080)", "fe": 0.010, "clay": 0.080, "desc": "ขอบทางลาดตะวันตกเฉียงเหนือ จุดสังเกตการณ์ขอบนอก"}
]

# -------------------------------------------------------------
# FIGURE 1: HIGH-RES R1 TOPOGRAPHY & DRILL CANDIDATES MAP
# -------------------------------------------------------------
fig = plt.figure(figsize=(18, 9), facecolor='#0f172a')

# Subplot 1: Elevation Map with R1 & Candidates
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_facecolor('#1e293b')

# Extract sub-grid around R1 with margin (E=779150-779750, N=2021350-2021800)
margin_e = (779150, 779750)
margin_n = (2021350, 2021800)

r_top, c_left = ds_elev.index(margin_e[0], margin_n[1])
r_bottom, c_right = ds_elev.index(margin_e[1], margin_n[0])
sub_elev = elev[min(r_top, r_bottom):max(r_top, r_bottom), min(c_left, c_right):max(c_left, c_right)]
sub_extent = [margin_e[0], margin_e[1], margin_n[0], margin_n[1]]

# Smooth elevation for contours
sub_elev_smooth = gaussian_filter(sub_elev, sigma=1.0)

# Hillshade calculation
gy, gx = np.gradient(sub_elev_smooth, 30, 30)
slope_rad = np.arctan(np.hypot(gx, gy))
aspect_rad = np.arctan2(-gx, gy)
az_sun = np.radians(315)
alt_sun = np.radians(45)
shaded = np.sin(alt_sun) * np.cos(slope_rad) + np.cos(alt_sun) * np.sin(slope_rad) * np.cos(az_sun - aspect_rad)
shaded = np.clip(shaded, 0, 1)

# Plot hillshade and elevation
im1 = ax1.imshow(sub_elev_smooth, extent=sub_extent, cmap='terrain', alpha=0.85, vmin=340, vmax=420)
ax1.imshow(shaded, extent=sub_extent, cmap='gray', alpha=0.35)

# Elevation contour lines
cs = ax1.contour(np.linspace(margin_e[0], margin_e[1], sub_elev.shape[1]),
                 np.linspace(margin_n[1], margin_n[0], sub_elev.shape[0]),
                 sub_elev_smooth, levels=np.arange(340, 430, 10), colors='#ffffff', linewidths=0.8, alpha=0.4)
ax1.clabel(cs, inline=True, fontsize=8, fmt='%d m', colors='#f8fafc')

# Draw R1 Pixel Footprint (3.92 ha)
for ex, ny in zip(r1_eastings, r1_northings):
    rect = plt.Rectangle((ex - 10, ny - 10), 20, 20, facecolor='#f59e0b', edgecolor='#d97706', alpha=0.45, linewidth=0.5)
    ax1.add_patch(rect)

# Plot Candidates
colors = {1: '#ef4444', 2: '#f97316', 3: '#3b82f6'}  # Rank 1=Red, Rank 2=Orange, Rank 3=Blue
for c in candidates:
    clr = colors[c['rank']]
    ax1.scatter(c['e'], c['n'], s=140, c=clr, edgecolors='#ffffff', linewidths=2.0, zorder=10)
    # Label text
    txt = ax1.text(c['e'] + 12, c['n'] + 6, f"{c['id']} ({c['elev']:.0f}m)",
                   fontsize=9, weight='bold', color='#ffffff', zorder=12,
                   path_effects=[pe.withStroke(linewidth=3, foreground='#000000')])

ax1.set_xlim(margin_e)
ax1.set_ylim(margin_n)
ax1.set_title("R1 Cover-Review Patch (3.92 ha) & 10 Candidate Drill Targets\nElevation, Hillshade & Topographic Contours (UTM 47N)", color='#f8fafc', fontsize=12, pad=12, weight='bold')
ax1.set_xlabel("UTM 47N Easting (m)", color='#94a3b8', fontsize=10)
ax1.set_ylabel("UTM 47N Northing (m)", color='#94a3b8', fontsize=10)
ax1.tick_params(colors='#94a3b8', labelsize=8)
ax1.grid(color='#334155', linestyle='--', alpha=0.5)

# Colorbar for elevation
cb1 = plt.colorbar(im1, ax=ax1, fraction=0.035, pad=0.03)
cb1.set_label('Elevation (m ASL)', color='#94a3b8', fontsize=9)
cb1.ax.tick_params(colors='#94a3b8', labelsize=8)

# Legend
leg_elements = [
    Patch(facecolor='#f59e0b', edgecolor='#d97706', alpha=0.6, label='R1 Boundary (3.92 ha, 98 px)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ef4444', markersize=9, label='Priority Rank 1 (Primary Core)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#f97316', markersize=8, label='Priority Rank 2 (Flank Targets)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#3b82f6', markersize=7, label='Priority Rank 3 (Outer Margins)')
]
ax1.legend(handles=leg_elements, loc='lower left', facecolor='#1e293b', edgecolor='#475569', labelcolor='#f8fafc', fontsize=8.5)

# Subplot 2: Mineral Signature & Geological Vectors Map
ax2 = fig.add_subplot(1, 2, 2)
ax2.set_facecolor('#1e293b')

# Background: Slope
r_top_s, c_left_s = ds_slope.index(margin_e[0], margin_n[1])
r_bottom_s, c_right_s = ds_slope.index(margin_e[1], margin_n[0])
sub_slope = slope[min(r_top_s, r_bottom_s):max(r_top_s, r_bottom_s), min(c_left_s, c_right_s):max(c_left_s, c_right_s)]
im2 = ax2.imshow(sub_slope, extent=sub_extent, cmap='magma', alpha=0.8, vmin=0, vmax=35)

# Draw R1 boundary
for ex, ny in zip(r1_eastings, r1_northings):
    rect = plt.Rectangle((ex - 10, ny - 10), 20, 20, facecolor='none', edgecolor='#38bdf8', alpha=0.4, linewidth=0.6)
    ax2.add_patch(rect)

# Draw Geological Structural Lineament Vector (Inferred Fault / Quartz Vein trend: NE-SW)
ax2.annotate("", xy=(779630, 2021670), xytext=(779330, 2021470),
             arrowprops=dict(arrowstyle="<->", color="#38bdf8", lw=3.0, ls="--"))
ax2.text(779340, 2021480, "Inferred Hydrothermal Structural Trend (NE-SW)",
         color='#38bdf8', fontsize=8.5, weight='bold',
         path_effects=[pe.withStroke(linewidth=3, foreground='#000000')])

# Draw proposed drill vectors (Azimuth & Dip arrows) for Rank 1 targets
# C10: Azimuth 225 deg (SW)
ax2.annotate("", xy=(779502 - 50, 2021538 - 50), xytext=(779502, 2021538),
             arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
ax2.text(779502 - 45, 2021538 - 65, "DH-R1-01 (Az: 225°, Dip: -55°)", color='#fca5a5', fontsize=8, weight='bold',
         path_effects=[pe.withStroke(linewidth=2.5, foreground='#000000')])

# C07: Azimuth 240 deg (WSW)
ax2.annotate("", xy=(779535 - 55, 2021585 - 30), xytext=(779535, 2021585),
             arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5))
ax2.text(779535 - 55, 2021585 - 45, "DH-R1-02 (Az: 240°, Dip: -50°)", color='#fca5a5', fontsize=8, weight='bold',
         path_effects=[pe.withStroke(linewidth=2.5, foreground='#000000')])

# Plot candidates with rank badges
for c in candidates:
    clr = colors[c['rank']]
    ax2.scatter(c['e'], c['n'], s=120, c=clr, edgecolors='#ffffff', linewidths=1.8, zorder=10)
    ax2.text(c['e'] + 10, c['n'] + 5, f"{c['id']}", fontsize=9, weight='bold', color='#ffffff', zorder=12,
             path_effects=[pe.withStroke(linewidth=3, foreground='#000000')])

ax2.set_xlim(margin_e)
ax2.set_ylim(margin_n)
ax2.set_title("Slope Map, Structural Trend & Proposed Drill Vectors\n(Steep Flanks vs Flat Summits)", color='#f8fafc', fontsize=12, pad=12, weight='bold')
ax2.set_xlabel("UTM 47N Easting (m)", color='#94a3b8', fontsize=10)
ax2.set_ylabel("UTM 47N Northing (m)", color='#94a3b8', fontsize=10)
ax2.tick_params(colors='#94a3b8', labelsize=8)
ax2.grid(color='#334155', linestyle='--', alpha=0.5)

cb2 = plt.colorbar(im2, ax=ax2, fraction=0.035, pad=0.03)
cb2.set_label('Slope Degrees', color='#94a3b8', fontsize=9)
cb2.ax.tick_params(colors='#94a3b8', labelsize=8)

plt.tight_layout()
fig.savefig('visuals/r1_candidates_map.png', dpi=200, facecolor='#0f172a')
plt.close(fig)
print("[Saved] visuals/r1_candidates_map.png")

# -------------------------------------------------------------
# FIGURE 2: EMIT MINERAL COMPARISON BAR CHART ACROSS C1-C10
# -------------------------------------------------------------
fig2, ax = plt.subplots(figsize=(14, 6), facecolor='#0f172a')
ax.set_facecolor('#1e293b')

c_ids = [c['id'] for c in candidates]
fe_depths = [c['fe'] for c in candidates]
clay_depths = [c['clay'] for c in candidates]
x_pos = np.arange(len(c_ids))
width = 0.38

rects1 = ax.bar(x_pos - width/2, fe_depths, width, label='Goethite + Jarosite + Quartz (Fe3+ Gossan Cap)', color='#eab308', edgecolor='#ca8a04')
rects2 = ax.bar(x_pos + width/2, clay_depths, width, label='Kaolinite + Muscovite + Dickite (Al-OH Hydrothermal Clay)', color='#38bdf8', edgecolor='#0284c7')

ax.set_xlabel('Candidate Drill Target ID', color='#f8fafc', fontsize=11, labelpad=10, weight='bold')
ax.set_ylabel('EMIT Absorption Band Depth', color='#f8fafc', fontsize=11, labelpad=10, weight='bold')
ax.set_title('NASA EMIT Hyperspectral Mineral Signatures at R1 Candidates\n(Direct Sensor Detection on 2025-01-22 Clear Sky Image)', color='#f8fafc', fontsize=13, pad=15, weight='bold')
ax.set_xticks(x_pos)
ax.set_xticklabels([f"{c['id']}\n(Rank {c['rank']})" for c in candidates], color='#cbd5e1', fontsize=9.5)
ax.tick_params(colors='#cbd5e1')
ax.grid(axis='y', color='#334155', linestyle='--', alpha=0.7)

# Add values on top of bars
for r in rects1:
    h = r.get_height()
    if h > 0:
        ax.annotate(f'{h:.3f}', xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha='center', va='bottom', fontsize=8, color='#fef08a', weight='bold')
for r in rects2:
    h = r.get_height()
    if h > 0:
        ax.annotate(f'{h:.3f}', xy=(r.get_x() + r.get_width() / 2, h), xytext=(0, 3),
                    textcoords="offset points", ha='center', va='bottom', fontsize=8, color='#bae6fd', weight='bold')

ax.legend(facecolor='#0f172a', edgecolor='#475569', labelcolor='#f8fafc', fontsize=10, loc='upper right')
ax.set_ylim(0, 0.24)

# Highlight C10 & C07
ax.annotate('★ PEAK ANOMALY (DH-R1-01 Target)', xy=(0 - width/2, 0.20), xytext=(1.2, 0.21),
            color='#f87171', fontsize=9, weight='bold',
            arrowprops=dict(arrowstyle="->", color="#f87171", lw=1.5))

plt.tight_layout()
fig2.savefig('visuals/r1_mineral_chart.png', dpi=200, facecolor='#0f172a')
plt.close(fig2)
print("[Saved] visuals/r1_mineral_chart.png")

# -------------------------------------------------------------
# EXPORT GEOJSON & KML FOR GOOGLE EARTH
# -------------------------------------------------------------
geojson_data = {
    "type": "FeatureCollection",
    "name": "R1_Drill_Candidates_Site02",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": []
}

for c in candidates:
    feature = {
        "type": "Feature",
        "properties": {
            "ID": c["id"],
            "Easting_m": c["e"],
            "Northing_m": c["n"],
            "Elev_m": c["elev"],
            "Slope_deg": c["slope"],
            "Priority": f"Rank {c['rank']}",
            "Mineral_Signature": c["mineral"],
            "Description": c["desc"]
        },
        "geometry": {
            "type": "Point",
            "coordinates": [c["lon"], c["lat"], c["elev"]]
        }
    }
    geojson_data["features"].append(feature)

with open('visuals/r1_candidates.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, indent=2, ensure_ascii=False)
print("[Saved] visuals/r1_candidates.geojson")

# Save KML
kml_content = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<kml xmlns="http://www.opengis.net/kml/2.2">',
    '<Document>',
    '  <name>R1 Drill Candidates - Site 02 Laos</name>',
    '  <description>10 Candidate Drill Targets derived from NASA EMIT Hyperspectral and Site 02 data</description>'
]

for c in candidates:
    kml_content.extend([
        '  <Placemark>',
        f'    <name>{c["id"]} (Rank {c["rank"]})</name>',
        f'    <description><![CDATA[<b>Elevation:</b> {c["elev"]} m<br><b>Slope:</b> {c["slope"]}°<br><b>Minerals:</b> {c["mineral"]}<br><b>Note:</b> {c["desc"]}]]></description>',
        '    <Point>',
        f'      <coordinates>{c["lon"]},{c["lat"]},{c["elev"]}</coordinates>',
        '    </Point>',
        '  </Placemark>'
    ])

kml_content.extend(['</Document>', '</kml>'])

with open('visuals/r1_candidates.kml', 'w', encoding='utf-8') as f:
    f.write('\n'.join(kml_content))
print("[Saved] visuals/r1_candidates.kml")

print("\nAll visualizations and spatial exports completed successfully!")
