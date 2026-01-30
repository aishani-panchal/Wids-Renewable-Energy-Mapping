import ee
import folium
#authentication
try:
    ee.Initialize(project='wids-earth-engine')
except:
    ee.Authenticate()
    ee.Initialize(project='wids-earth-engine')
    
#define region (I used feature collection to define the area)
gaul = ee.FeatureCollection("FAO/GAUL/2015/level2")
mh = gaul.filter(ee.Filter.eq("ADM1_NAME", "Maharashtra"))
districts = ["Jalgaon", "Dhule", "Nandurbar"]
roi = mh.filter(ee.Filter.inList("ADM2_NAME", districts))
geometry = roi.geometry()

#image data from Sentinel 2
s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
cs_plus = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")
cs_bands = cs_plus.first().bandNames()

start = "2023-01-01"
end   = "2024-01-01"

#basic cloud filtering to take images with less than 40%cloud
filtered = (s2
            .filterBounds(geometry)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 40)))

#advance cloud filtering
# Link CS+ bands 
s2cs = filtered.linkCollection(cs_plus, cs_bands)
# Cloud mask function
def mask_cloud(image):
    mask = image.select("cs").gte(0.5)
    return image.updateMask(mask)

s2_clean = (s2cs
            .map(mask_cloud)
            .select("B.*")
            .median()
            .clip(geometry))

#terrain (slope)
dem = ee.Image("USGS/SRTMGL1_003").clip(geometry)
slope  = ee.Terrain.slope(dem)
aspect = ee.Terrain.aspect(dem)

#NDVI (gives vegatation and land image)
ndvi = s2_clean.normalizedDifference(["B8", "B4"]).rename("NDVI")

# ERA5 (GHI + Temperature)
era5 = (ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
        .filterBounds(geometry)
        .filterDate(start, end)
        .median()
        .clip(geometry))

ghi = era5.select("surface_solar_radiation_downwards_sum").rename("GHI")
temp = era5.select("temperature_2m").subtract(273.15).rename("Temp")

# Land Cover (ESA WorldCover)
landcover = ee.Image("ESA/WorldCover/v100/2020").select("Map").clip(geometry)

# Feature Stack
stack = (s2_clean.select(["B2", "B3", "B4", "B8"])
         .addBands([ndvi, slope.rename("Slope"), aspect.rename("Aspect"),
                    ghi, temp, landcover.rename("LC")]))
                    

# TRAINING POLYGONS
good_poly = ee.Geometry.Rectangle([74.42, 20.97, 74.45, 21.00])
bad_poly  = ee.Geometry.Rectangle([74.80, 20.80, 75.0, 21.10])

training_fc = ee.FeatureCollection([
    ee.Feature(good_poly, {"class": 1}),
    ee.Feature(bad_poly,  {"class": 0})
])

training = stack.sampleRegions(
    collection=training_fc,
    properties=["class"],
    scale=30
)

# Gradient Tree Boosting
classifier = ee.Classifier.smileGradientTreeBoost(
    numberOfTrees=200,
    shrinkage=0.05,
    maxNodes=30
).train(
    features=training,
    classProperty="class",
    inputProperties=stack.bandNames()
)

classified = stack.classify(classifier)

# SPLIT INTO SMALL vs LARGE SOLAR PV
small_pv = classified.eq(1).And(slope.lt(8))
large_pv = classified.eq(1).And(slope.lt(5)).And(ndvi.lt(0.3))

solar_class = (ee.Image(0)
               .where(small_pv, 1)
               .where(large_pv, 2)
               .rename("SolarSuitability"))

# FOLIUM MAP DISPLAY
def add_ee_layer(self, ee_object, vis_params, name):
    map_id_dict = ee.Image(ee_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

folium.Map.add_ee_layer = add_ee_layer

# Center map on ROI
center = geometry.centroid().coordinates().getInfo()
map = folium.Map(location=[center[1], center[0]], zoom_start=9)

# Add layers
s2_vis = {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000}
map.add_ee_layer(s2_clean, s2_vis, "Sentinel-2")

palette = ["#9e9e9e", "#ffd54f", "#fb8c00"]
classified_vis = {"min": 0, "max": 2, "palette": palette}
map.add_ee_layer(solar_class, classified_vis, "Solar PV Suitability")

roi_vis = {"color": "blue", "fillColor": "00000000"}
map.add_ee_layer(roi, roi_vis, "Khandesh Boundary")

map
