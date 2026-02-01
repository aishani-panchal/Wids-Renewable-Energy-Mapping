# Wids-Midterm (Renewable Energy Smart Mapping)
This project explores how satellite imagery, climate data, and machine learning can be combined to identify areas with potential for solar and wind energy.
The workflow is implemented using Google Earth Engine and Python and the results are visualized through an interactive Folium map

This project attempts to:
Combine satellite data, terrain, and climate information
Use machine learning to learn patterns from labelled examples
Produce a visual map highlighting zones with higher solar or wind potential

1. Study Area
   Region: Khandesh Corridor, Maharashtra, India
   this includes 3 districs (Jalgaon, Dhule, Nandurbar)
   Coordinates: [74.0, 20.5, 75.5, 21.5]
2. Data used:I used a combination of satellite and climate products:
   Sentinel-2: Optical imagery (cloud-masked)
   Cloud Score Plus to remove cloudy pixels more effectively
   SRTM Digital Elevation Model to derive terrain features like slope and aspect
   ERA5-Land to estimateincoming solar radiation (used as a proxy for GHI)
   ESA WorldCover 2020 to understand land-use and land-cover patterns

3. Time: All data were collected for the period January 2023 to January 2024.
4. Features created
  I created a set of features that are more meaningful for solar-site assessment
  Sentinel-2 bands: B2, B3, B4, B8, NDVI, which helps indicate vegetation cover, Slope and     Aspect from elevation data
6. Method I used: Training samples created using polygons
  Tree boosting  classifier used for suitability mapping
  
7. Final output
   The result is an interactive map showing:
     Base satellite imagery
     Potential large solar zones (orange)
     Potential small solar zones (yellow)
9. Limitations 
   No external ground-truth dataset is used
   Accuracy assessment is internal

# Accuracy
Since no external ground-truth dataset exists for renewable energy suitability, the model is evaluated using an internal accuracy assessment approach.
The labelled samples are randomly split into:
70% training data
30% validation data

Metrics used
1. Confusion Matrix – to examine class-wise performance
2. Overall Accuracy – percentage of correctly classified samples
3. Kappa Coefficient – agreement beyond chance
4. Training (resubstitution) accuracy is also reported for reference, while validation accuracy is treated as the primary performance indicator.

Interpretation

The accuracy results reflect the model’s consistency in learning the provided labels, not real-world installation feasibility.
Moderate accuracy values are expected due to limited training samples and the exploratory nature of the study.
Field surveys and policy constraints are not included
