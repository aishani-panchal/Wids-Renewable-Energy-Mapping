import ee
import geemap

# Authenticate
try:
    ee.Initialize(project='wids-earth-engine')
except:
    ee.Authenticate()
    ee.Initialize(project='wids-earth-engine')

# ROI
roi = ee.Geometry.Rectangle([74.0, 20.5, 75.5, 21.5])

# NEW: Sentinel-2 cloud masking function (borrowed conceptually)
def mask_s2_sr(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)

# Sentinel-2 data
s2 = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(roi)
    .filterDate('2023-01-01', '2023-05-30')
    .map(mask_s2_sr)    
    .median()
    .clip(roi)
)

# DEM & slope
dem = ee.Image('USGS/SRTMGL1_003').clip(roi)
slope = ee.Terrain.slope(dem)

# ERA5
climate = (
    ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY_AGGR")
    .filterBounds(roi)
    .filterDate('2023-01-01', '2023-12-31')
    .median()
    .clip(roi)
)

# NDVI
ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')

# Wind speed
wind_speed = climate.select('u_component_of_wind_10m') \
    .hypot(climate.select('v_component_of_wind_10m')) \
    .rename('WindSpeed')

# Solar radiation
ghi = climate.select('surface_solar_radiation_downwards_sum').rename('GHI')

# Feature stack
feature_stack = s2.select(['B2', 'B3', 'B4', 'B8']) \
    .addBands([ndvi, slope, wind_speed, ghi])

# OPTIONAL UPGRADE: polygon-based training (recommended)
solar_poly = ee.Geometry.Rectangle([74.42, 20.97, 74.45, 21.00])
wind_poly = ee.Geometry.Rectangle([74.22, 21.07, 74.25, 21.10])
neg_poly = ee.Geometry.Rectangle([74.75, 20.85, 74.90, 21.05])

training_fc = ee.FeatureCollection([
    ee.Feature(solar_poly, {'class': 1}),
    ee.Feature(wind_poly, {'class': 2}),
    ee.Feature(neg_poly, {'class': 0}),
])

training = feature_stack.sampleRegions(
    collection=training_fc,
    properties=['class'],
    scale=30
)

# Classifier (RF retained — best for mixed data)
classifier = ee.Classifier.smileRandomForest(100).train(
    training, 'class', feature_stack.bandNames()
)

classified = feature_stack.classify(classifier)

# Smart filtering
solar_sites = classified.eq(1).And(slope.lt(5))
wind_sites = classified.eq(2).And(wind_speed.gt(2))

# Map
Map = geemap.Map(center=[21.1, 74.5], zoom=9)
Map.addLayer(s2, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3}, 'Sentinel-2')
Map.addLayer(solar_sites.selfMask(), {'palette': ['orange']}, 'Solar')
Map.addLayer(wind_sites.selfMask(), {'palette': ['blue']}, 'Wind')

Map.add_legend(
    title="Renewable Energy Suitability",
    labels=['Solar Potential', 'Wind Potential'],
    colors=[(255,165,0), (0,0,255)]
)

Map