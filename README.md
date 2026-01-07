# Wids-Midterm (Renewable Energy Smart Mapping)
This project explores how satellite imagery, climate data, and machine learning can be combined to identify areas with potential for solar and wind energy.
The workflow is implemented using Google Earth Engine and Python. 

This project attempts to:
Combine satellite data, terrain, and climate information
Use machine learning to learn patterns from labelled examples
Produce a visual map highlighting zones with higher solar or wind potential

1. Study Area
   Region: Khandesh Corridor, Maharashtra, India
   Coordinates: [74.0, 20.5, 75.5, 21.5]
2. Data used
   Sentinel-2: Optical imagery (cloud-masked)
   SRTM DEM: Terrain and slope
   ERA5-Land: Wind speed and solar radiation
3. Features created
   Instead of relying only on raw imagery, several meaningful features are derived: Spectral bands (B2, B3, B4, B8),NDVI (vegetation indicator), Slope (from elevation), Wind speed, Global Horizontal Irradiance (GHI)
4. Method I used: Training samples created using polygons
   Random Forest classifier used for suitability mapping
   Solar zones are limited to low-slope areas
   Wind zones are restricted to higher wind speeds to remove unrealistic problems
5. Final output
   The result is an interactive map showing:
     Base satellite imagery
     Potential solar zones (orange)
     Potential wind zones (blue)
7. Limitations 
   No external ground-truth dataset is used
   Accuracy assessment is internal

# Accuracy
Since no external ground-truth dataset exists for renewable energy suitability, the model is evaluated using an internal accuracy assessment approach.
The labelled samples are randomly split into:
70% training data
30% validation data

A Random Forest classifier is trained using the training subset and evaluated on the unseen validation samples.

Metrics used
1. Confusion Matrix – to examine class-wise performance
2. Overall Accuracy – percentage of correctly classified samples
3. Kappa Coefficient – agreement beyond chance
4. Training (resubstitution) accuracy is also reported for reference, while validation accuracy is treated as the primary performance indicator.

Interpretation

The accuracy results reflect the model’s consistency in learning the provided labels, not real-world installation feasibility.
Moderate accuracy values are expected due to limited training samples and the exploratory nature of the study.
Field surveys and policy constraints are not included
