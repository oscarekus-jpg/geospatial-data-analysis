import geopandas as gpd
import osmnx as ox
import shapely

#defining a place (my city, in this case: New York City)

current_place_name = "New York City, United States"

#Now I will fetch all the public parks from Open Street Map
parks_nyc = ox.features_from_place(current_place_name, tags={'leisure': 'park'})

#checking what got fetched

print(f"Total parks found: {len(parks_nyc)}")
print(parks_nyc.head()[['name', 'geometry']])
#Check the crs if needed: print(parks_nyc.crs)
#CHeck the geometries if needed: print(parks_nyc.geometry.geom_type.value_counts())
#Check th column names if needed: print(parks_nyc.columns.tolist())

#will filter out to only have the polygons, as parks are registeres as points also...

parks_polygons = parks_nyc[parks_nyc.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])]

#fetching transit stops:
transit_stops = ox.features_from_place(current_place_name, tags={'highway': 'bus_stop'})

#reproject the layers to a metric crs:
metric_crs = 'EPSG:3857'
parks_reprojected = parks_polygons.to_crs(metric_crs)
transit_reprojected = transit_stops.to_crs(metric_crs)

#generating a 200m buffer around every park polygon, because the bus stops usually do not sit inside a park...

parks_reprojected['buffer_geom'] = parks_reprojected.geometry.buffer(200)

#Checking the data:
first_park_area = parks_reprojected.geometry.iloc[0].area
first_buffer_area = parks_reprojected['buffer_geom'].iloc[0].area 

print(f"Original Park Area: {first_park_area} sq meters")
print(f"200m Buffered Area: {first_buffer_area} sq meters")

#Setting the geom for the parks to the actual one that has the buffer:
buffer_gdf_parks = parks_reprojected.set_geometry('buffer_geom')

#doing a spatial join, this checks which bus stops are within the buffer polygons
stops_near_parks = gpd.sjoin(
    transit_reprojected,
    buffer_gdf_parks[['name','buffer_geom']],
    how= 'inner',
    predicate= 'within'
)

#Ccheckin the results of the join:
print(f"All bus stops:{transit_reprojected}.")
print(f"buffer transit stops:{stops_near_parks}")
print(stops_near_parks[['name_left','name_right']].head())



import folium
from folium.plugins import MarkerCluster

# 1. Give each park a truly unique ID so unnamed parks are counted individually
parks_reprojected = parks_reprojected.reset_index(drop=True)
parks_reprojected['park_id'] = parks_reprojected.index

# 2. Re-run spatial join with unique park_id
buffer_gdf_parks = gpd.GeoDataFrame(
    parks_reprojected[['park_id', 'name']], 
    geometry=parks_reprojected['buffer_geom'], 
    crs=metric_crs
)

stops_near_parks = gpd.sjoin(
    transit_reprojected,
    buffer_gdf_parks,
    how='inner',
    predicate='within'
)

# 3. Calculate transit counts strictly per unique park_id
park_stop_counts = stops_near_parks.groupby('park_id').size().to_dict()

# 4. Prepare Park Polygons & assign accurate counts
parks_map = parks_reprojected.set_geometry('geometry')[['park_id', 'name', 'geometry']].to_crs("EPSG:4326")
parks_map['transit_count'] = parks_map['park_id'].map(lambda pid: park_stop_counts.get(pid, 0))
parks_map['display_name'] = parks_map['name'].fillna("Unnamed Green Space")

# 5. Prepare Buffers & Stops
buffers_map = buffer_gdf_parks[['park_id', 'name', 'geometry']].to_crs("EPSG:4326")
stops_map = stops_near_parks[['name_left', 'name_right', 'geometry']].to_crs("EPSG:4326")

# Strict geometry cleanup
parks_map = parks_map[parks_map.geometry.notnull() & ~parks_map.geometry.is_empty]
buffers_map = buffers_map[buffers_map.geometry.notnull() & ~buffers_map.geometry.is_empty]
stops_map = stops_map[stops_map.geometry.notnull() & ~stops_map.geometry.is_empty]

# Deduplicate points sharing identical coordinates
stops_map['coord_key'] = stops_map.geometry.apply(lambda geom: f"{geom.x:.6f}_{geom.y:.6f}")
stops_unique = stops_map.drop_duplicates(subset=['coord_key']).copy()

# 6. Initialize Map
nyc_center = [40.7831, -73.9712]
m = folium.Map(location=nyc_center, zoom_start=12, tiles="CartoDB positron")

def get_color(count):
    if count == 0:
        return "#94A3B8"  # Slate Gray (0 stops)
    elif count < 5:
        return "#FDE047"  # Yellow (1-4 stops)
    elif count < 15:
        return "#F59E0B"  # Amber (5-14 stops)
    else:
        return "#B91C1C"  # Deep Autumn Red (15+ stops)

# Layer 1: 200m Buffers (toggleable)
fg_buffers = folium.FeatureGroup(name="200m Park Buffers", show=False)
folium.GeoJson(
    buffers_map[['name', 'geometry']],
    style_function=lambda x: {
        "fillColor": "#FDE68A",
        "color": "#D97706",
        "weight": 1,
        "fillOpacity": 0.25,
        "dashArray": "3, 3"
    }
).add_to(fg_buffers)
fg_buffers.add_to(m)

# Layer 2: Autumn Parks (Accurately Scored)
fg_parks = folium.FeatureGroup(name="Autumn Parks (Transit Accessibility)", show=True)
folium.GeoJson(
    parks_map,
    style_function=lambda feature: {
        "fillColor": get_color(feature['properties']['transit_count']),
        "color": "#78350F",
        "weight": 1.5,
        "fillOpacity": 0.75
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['display_name', 'transit_count'],
        aliases=['Park:', 'Bus Stops within 200m:'],
        localize=True
    )
).add_to(fg_parks)
fg_parks.add_to(m)

# Layer 3: Bus Stops
fg_stops = folium.FeatureGroup(name="Transit Stops", show=True)
marker_cluster = MarkerCluster(
    options={
        'maxClusterRadius': 35,
        'disableClusteringAtZoom': 15,
        'spiderfyOnMaxZoom': True
    }
).add_to(fg_stops)

for _, row in stops_unique.iterrows():
    stop_label = str(row['name_left']) if str(row['name_left']) != 'nan' else 'Bus Stop'
    park_label = str(row['name_right']) if str(row['name_right']) != 'nan' else 'Nearby Green Space'
    
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color="#0369A1",
        fill=True,
        fill_color="#38BDF8",
        fill_opacity=0.9,
        weight=1.5,
        popup=folium.Popup(f"<b>Stop:</b> {stop_label}<br><b>Park:</b> {park_label}", max_width=250)
    ).add_to(marker_cluster)

fg_stops.add_to(m)

# Layer Switcher
folium.LayerControl(collapsed=False).add_to(m)

# On-screen Legend
legend_html = """
<div style="
    position: fixed; 
    bottom: 30px; 
    left: 30px; 
    width: 220px; 
    background-color: white; 
    z-index: 9999; 
    border: 2px solid #CBD5E1; 
    border-radius: 8px; 
    padding: 10px 14px; 
    font-size: 12px; 
    font-family: sans-serif;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
">
    <b style="font-size: 13px; color: #0F172A;">Park Transit Access</b><br>
    <span style="color: #64748B; font-size: 11px;">Stops within 200m</span>
    <div style="margin-top: 8px;">
        <i style="background: #B91C1C; width: 14px; height: 14px; float: left; margin-right: 8px; border-radius: 2px;"></i> 15+ Stops (High)<br>
        <i style="background: #F59E0B; width: 14px; height: 14px; float: left; margin-right: 8px; border-radius: 2px; margin-top: 3px;"></i> 5 – 14 Stops (Med)<br>
        <i style="background: #FDE047; width: 14px; height: 14px; float: left; margin-right: 8px; border-radius: 2px; margin-top: 3px;"></i> 1 – 4 Stops (Low)<br>
        <i style="background: #94A3B8; width: 14px; height: 14px; float: left; margin-right: 8px; border-radius: 2px; margin-top: 3px;"></i> 0 Stops<br>
        <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 6px 0;">
        <i style="background: #38BDF8; width: 10px; height: 10px; border-radius: 50%; float: left; margin-right: 10px; margin-top: 2px; border: 1px solid #0369A1;"></i> Bus Stop Pin
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Save output
m.save("autumn_park_transit_map.html")
print("Map updated with accurate unique-park transit scoring: autumn_park_transit_map.html")

#used url= file:///Users/owozniczka/Desktop/Oscars_Stuff/autumn_park_transit_map.html