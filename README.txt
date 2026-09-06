# Geospatial Analysis Portfolio

A collection of Python-based geospatial projects exploring vector analysis, spatial SQL, spatial indexing, interactive visualization, and remote sensing.

The projects were developed as practical exercises in working with real-world geospatial datasets and open geospatial technologies.

## Projects

### 01 — Autumn Park & Transit

**Focus:** Vector GIS, spatial joins, accessibility analysis

An analysis of public parks and bus-stop accessibility in New York City using OpenStreetMap data.

The workflow:

* Retrieves park and bus-stop data from OpenStreetMap using OSMnx
* Filters and prepares park geometries with GeoPandas
* Reprojects the data to a metric coordinate system
* Creates 200 m buffers around parks
* Uses spatial joins to identify nearby bus stops
* Calculates the number of transit stops associated with each park
* Produces an interactive Folium map with park accessibility scores, buffers, and clustered transit stops

**Main technologies:** Python, GeoPandas, OSMnx, Shapely, Folium

---

### 02 — Energy Systems & Spatial SQL

**Focus:** Spatial SQL, cloud-hosted data, aggregation, H3 spatial indexing

An exploration of global power-plant data using DuckDB and its spatial extension.

The workflow:

* Queries the Global Power Plant Database directly from a remote CSV source
* Uses DuckDB Spatial to create and analyse geographic point geometries
* Filters power plants by location and energy source
* Aggregates plant counts and generating capacity
* Exports selected regional results to GeoJSON
* Uses Uber's H3 spatial indexing system to aggregate global energy production into hexagonal cells
* Stores the resulting spatial dataset as Parquet
* Creates an interactive 3D visualization using PyDeck

**Main technologies:** Python, DuckDB, Spatial SQL, H3, Parquet, GeoJSON, PyDeck

---

### 03 — Tracking Autumn from Space

**Focus:** Remote sensing, STAC, Sentinel-2, NDVI

A remote-sensing workflow for analysing vegetation conditions in the Tatra Mountains during autumn 2025.

The workflow:

* Connects to the Microsoft Planetary Computer STAC API
* Searches Sentinel-2 L2A imagery for a defined area and time period
* Filters scenes based on cloud cover
* Retrieves Sentinel-2 red (B04) and near-infrared (B08) bands
* Calculates NDVI from the raster data
* Crops the resulting raster to the area of interest
* Visualizes the NDVI results
* Exports the processed raster as a GeoTIFF

**Main technologies:** Python, STAC, Sentinel-2, rioxarray, Planetary Computer, Matplotlib

---

## Skills Demonstrated

Across the projects, the portfolio demonstrates experience with:

* Geospatial data acquisition
* Vector and raster data processing
* Coordinate reference systems and reprojection
* Spatial joins and buffering
* Spatial SQL
* Remote geospatial datasets
* H3 spatial indexing
* GeoJSON and Parquet
* Interactive web mapping
* Remote sensing workflows
* NDVI calculation
* Reproducible Python-based geospatial analysis
