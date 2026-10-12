from pathlib import Path
import json, warnings, shutil, hashlib, zipfile
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import matplotlib.patheffects as pe
from matplotlib.ticker import MultipleLocator
from scipy.ndimage import binary_dilation
from shapely.geometry import Polygon
import rasterio
from rasterio.plot import plotting_extent
from rasterio.enums import Resampling
from pystac_client import Client
import planetary_computer as pc
import stackstac

BUNDLE=Path(__file__).resolve().parent.parent
BASE=BUNDLE/'03_Data'
OUT=BUNDLE/'02_Maps/Map_Sheets';OUT.mkdir(exist_ok=True)
m=json.loads((BASE/'manifest.json').read_text())
d=np.load(next((BUNDLE/'04_Notebook/inputs').glob('cube_*.npz')))
r=d['reflectance'];scl=d['scl'];x=d['x'];y=d['y']
aoi=gpd.GeoDataFrame(geometry=[Polygon(m['aoi_coordinates'])],crs=4326).to_crs(32647)
def read(name):
    with rasterio.open(BUNDLE/'02_Maps'/name) as ds:return ds.read(1),ds.transform
eligible,tr=read('eligible_surface.tif');inside=np.isfinite(eligible)
review,_=read('historical_cover_disagreement.tif');score,_=read('relative_evidence.tif')
extent=plotting_extent(eligible,tr)
bad=~np.isin(scl,[4,5,6]);buffer=np.stack([binary_dilation(v,iterations=1) for v in bad])
clear=np.isin(scl,[4,5])&~buffer&np.all(np.isfinite(r)&(r>0),axis=1)&inside
blue,green,red,nir,sw1,sw2=[r[:,i] for i in range(6)]
def ratio(a,b):return np.divide(a,b,out=np.full_like(a,np.nan),where=np.isfinite(a)&np.isfinite(b)&(b>0.01))
def median(a,mask):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',RuntimeWarning)
        return np.nanmedian(np.where(mask,a,np.nan),axis=0)
ndvi=ratio(nir-red,nir+red);ndwi=ratio(green-nir,green+nir)
exposed=clear&(scl==5)&(ndvi<.30)&(ndwi<0)&(sw1>.02)
ndvi_map=median(ndvi,clear)
swir_map=median(ratio(sw1,sw2),exposed)
iron_map=median(ratio(red,blue),exposed)
rgb=np.stack([median(red,clear),median(green,clear),median(blue,clear)],axis=-1)
for i in range(3):
    lo,hi=np.nanpercentile(rgb[:,:,i][inside],[2,98]);rgb[:,:,i]=np.clip((rgb[:,:,i]-lo)/(hi-lo),0,1)
rgb=np.nan_to_num(rgb,nan=.9)
vertices=np.asarray(aoi.geometry.iloc[0].exterior.coords)[:-1]
plt.rcParams.update({'font.size':10,'axes.titlesize':13})
def frame(ax):
    aoi.boundary.plot(ax=ax,color='white',linewidth=3)
    aoi.boundary.plot(ax=ax,color='#25333c',linewidth=1)
    ax.set_xlim(extent[:2]);ax.set_ylim(extent[2:]);ax.set_aspect('equal')
    ax.ticklabel_format(style='plain',useOffset=False);ax.tick_params(labelsize=8)
    ax.set_xlabel('Easting (m)');ax.set_ylabel('Northing (m)');ax.set_facecolor('#eceff1')
    ax.grid(alpha=.25)
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=200,facecolor='white',bbox_inches='tight')
    fig.savefig(OUT/(name+'.pdf'),facecolor='white',bbox_inches='tight')
    plt.close(fig)
def layer(name,data,title,cmap,limits,note,layer_extent=extent):
    fig,ax=plt.subplots(figsize=(9,11),layout='constrained')
    im=ax.imshow(data,extent=layer_extent,cmap=cmap,vmin=limits[0],vmax=limits[1],interpolation='nearest')
    frame(ax);fig.colorbar(im,ax=ax,shrink=.7)
    ax.set_title(title+'\nSite 02 | WGS 84 / UTM 47N')
    fig.supxlabel(note+'\nGrey = unavailable / excluded; spectral proxies are not gold detection.',fontsize=9)
    save(fig,name)
layer('02_NDVI',ndvi_map,'Median NDVI | clear land observations','RdYlGn',(-.2,.9),'8 dates: 21 Nov 2025 to 10 Apr 2026 | 20 m grid')
for name,data,title in [('03_SWIR_proxy',swir_map,'SWIR ratio B11 / B12'),('04_Iron_proxy',iron_map,'Red / blue ratio B04 / B02')]:
    finite=data[np.isfinite(data)];limits=np.percentile(finite,[2,98])
    layer(name,data,title,'magma',limits,'Exposed dates only, before historical-cover veto | raw ratio; display clipped at P2/P98')
layer('05_Relative_evidence',score,'Relative spectral evidence | strict eligible surfaces','magma',(0,1),'Joint percentile rank | 0 qualifying polygons | 20 m grid')
layer('06_Review_areas',np.where(review==1,1,np.nan),'Historical cover disagreement | 35.92 ha','autumn',(0,1),'Current repeated exposure vs 2021 reference | manual review areas, not mineral targets')
print('Spectral maps saved',flush=True)
cache=BUNDLE/'04_Notebook/inputs/dem_map_30m.npz'
if cache.exists():
    demcache=np.load(cache);demv=demcache['values'];dx=demcache['x'];dy=demcache['y'];demids=demcache['ids'].tolist()
else:
    catalog=Client.open('https://planetarycomputer.microsoft.com/api/stac/v1')
    items=list(catalog.search(collections=['cop-dem-glo-30'],intersects=Polygon(m['aoi_coordinates']).__geo_interface__).items())
    demids=[i.id for i in items]
    ds=stackstac.stack([pc.sign(i) for i in items],assets=['data'],bounds_latlon=Polygon(m['aoi_coordinates']).bounds,epsg=32647,resolution=30,rescale=False,resampling=Resampling.bilinear).compute()
    demv=np.nanmax(ds.values[:,0],axis=0);dx=ds.x.values;dy=ds.y.values
    np.savez_compressed(cache,values=demv,x=dx,y=dy,ids=np.array(demids))
dtr=rasterio.transform.from_origin(dx[0]-15,dy[0]+15,30,30)
from rasterio.features import geometry_mask
dinside=geometry_mask(aoi.geometry,out_shape=demv.shape,transform=dtr,invert=True)
gy,gx=np.gradient(demv,30,30);slope=np.degrees(np.arctan(np.hypot(gx,gy)))
dextent=plotting_extent(demv,dtr)
for name,data,title,cmap in [('07_Elevation',demv,'Copernicus GLO-30 surface elevation (m)','terrain'),('08_Slope',slope,'Surface-model slope (degrees)','magma')]:
    masked=np.where(dinside,data,np.nan)
    layer(name,masked,title,cmap,(float(np.nanmin(masked)),float(np.nanmax(masked))),'30 m UTM resampling | DSM includes canopy / structures; not surveyed ground',dextent)
    with rasterio.open(OUT/(name+'.tif'),'w',driver='GTiff',height=data.shape[0],width=data.shape[1],count=1,dtype='float32',crs='EPSG:32647',transform=dtr,nodata=np.nan,compress='deflate') as dst:dst.write(masked.astype('float32'),1)
fig=plt.figure(figsize=(11.7,16.5),facecolor='white')
fig.add_artist(Rectangle((.025,.025),.95,.95,transform=fig.transFigure,fill=False,linewidth=1.5))
fig.text(.5,.95,'SURFACE ANOMALY SCREENING MAP',ha='center',fontsize=19,weight='bold')
fig.text(.5,.925,'Site 02, Laos',ha='center',fontsize=14)
fig.text(.5,.902,'AOI: 43.053 km² | 0 qualifying polygons | Historical-cover review: 35.92 ha',ha='center',fontsize=10)
ax=fig.add_axes([.10,.32,.80,.56]);ax.imshow(rgb,extent=extent)
from matplotlib.colors import ListedColormap
ax.imshow(np.where(review==1,1,np.nan),extent=extent,cmap=ListedColormap(['#ff9f1c']),vmin=0,vmax=1,alpha=.8,interpolation='nearest')
ax.imshow(np.where(eligible==1,1,np.nan),extent=extent,cmap=ListedColormap(['#22b6b0']),vmin=0,vmax=1,alpha=.85,interpolation='nearest')
frame(ax);ax.xaxis.set_major_locator(MultipleLocator(2000));ax.yaxis.set_major_locator(MultipleLocator(2000))
ax.tick_params(top=True,right=True,labeltop=True,labelright=True)
for i,(vx,vy) in zip([1,2,4,3],vertices):
    ax.scatter(vx,vy,s=18,c='#b8ff53',edgecolors='black',zorder=9)
    ax.annotate(str(i),(vx,vy),xytext=(5,7),textcoords='offset points',fontsize=9,weight='bold',path_effects=[pe.withStroke(linewidth=3,foreground='white')])
ax.annotate('GN',xy=(.93,.94),xytext=(.93,.83),xycoords='axes fraction',ha='center',color='white',weight='bold',path_effects=[pe.withStroke(linewidth=3,foreground='black')],arrowprops={'arrowstyle':'-|>','color':'white','lw':2})
bx=extent[0]+400;by=extent[2]+350
ax.plot([bx,bx+1000],[by,by],color='black',lw=6)
ax.plot([bx,bx+500],[by,by],color='white',lw=4)
for dist,lab in [(0,'0'),(500,'500'),(1000,'1,000 m')]:ax.annotate(lab,(bx+dist,by),xytext=(0,8),textcoords='offset points',ha='center',color='white',fontsize=8,path_effects=[pe.withStroke(linewidth=2,foreground='black')])
info=fig.add_axes([.055,.055,.43,.22]);info.axis('off')
info.text(0,1,'MAP INFORMATION',weight='bold',fontsize=12,va='top')
info.text(0,.88,'Projection: WGS 84 / UTM Zone 47N\nImagery: 8 dates, 21 Nov 2025–10 Apr 2026\nAnalysis grid: 20 m | Land-cover reference: 2021\nEligible surface: 2.68 ha | Qualifying polygons: 0\nLabels: original screenshot vertex IDs\nGN: grid north | Method v3',va='top',linespacing=1.7,fontsize=10)
info.legend(handles=[Patch(color='#ff9f1c',label='Historical-cover disagreement'),Patch(color='#22b6b0',label='Eligible exposed surface')],loc='lower left',bbox_to_anchor=(0,.13),frameon=False,fontsize=9)
info.text(0,.10,'Reconnaissance observations; no gold confirmation.\nOrange areas require cover verification, not excavation.\nCRS assumed: confirm against survey before navigation.',va='top',fontsize=9,linespacing=1.5)
tabax=fig.add_axes([.55,.06,.39,.205]);tabax.axis('off');tabax.set_title('AOI VERTEX COORDINATES',fontsize=11,weight='bold')
table=tabax.table(cellText=[[i,f'{vx:.0f}',f'{vy:.0f}'] for i,(vx,vy) in zip([1,2,4,3],vertices)],colLabels=['Point','Easting','Northing'],cellLoc='center',bbox=[0,0,1,1]);table.auto_set_font_size(False);table.set_fontsize(9)
for (row,col),cell in table.get_celld().items():
    cell.set_edgecolor('#777');cell.set_linewidth(.5)
    if row==0:cell.set_facecolor('#eceff1');cell.set_text_props(weight='bold')
save(fig,'01_Field_map_sheet')
(OUT/'map_provenance.json').write_text(json.dumps({'source_manifest':'../../03_Data/manifest.json','dem_items':demids,'terrain_grid_m':30,'terrain_resampling':'bilinear','slope_method':'arctan magnitude of central finite differences; DSM, no ground-surface correction','spectral_display':'median per-date ratios on exposed surfaces before WorldCover veto; P2/P98 display clipping only','confirmed_gold_targets':0},indent=2))
print('All map sheets complete',flush=True)
