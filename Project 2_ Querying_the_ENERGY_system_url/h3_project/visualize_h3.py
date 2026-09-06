import duckdb
import pydeck as pdk

con = duckdb.connect()

con.sql("INSTALL h3 FROM community; LOAD h3;")

#pydeck needs the h3 index as a string not as an integer...
#also will only show plants that have significant power to not cluster the map

query4 = """
    SELECT  
        h3_h3_to_string(h3_index) AS hex_id,
        primary_fuel,
        total_megawatts
    FROM 'global_h3_energy_grid.parquet'
    WHERE total_megawatts > 100
"""
df4 = con.sql(query4).df()

print(f"loaded {len(df4)}.... rendering map....")

#defining the pydeck layer
layer = pdk.Layer(
    'H3HexagonLayer',
    df4,
    pickable=True,
    stroked=True,
    filled=True,
    extruded=True,
    get_hexagon='hex_id',
    #elevation based on the total megawatts
    get_elevation='total_megawatts',
    elevation_scale=15,
    #color scalem hoter - highier colors
    get_fill_color="[255, 255 - (total_megawatts / 100), 0, 200]",

)

#setting the starting point
view_state = pdk.ViewState(
    latitude=50.0647,
    longitude=19.9450,
    zoom=5,
    pitch=50, #tilts the camera for a 3d effect
    bearing=0
)

#rendering the map on a html file:
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "Primary Fuel: {primary_fuel}\nCapacity: {total_megawatts} MW"},
    map_provider="carto",
    map_style=pdk.map_styles.CARTO_DARK
)

r.to_html("3D_Global_energy_Grid.html")
print("3D map should be saved and GTG ! :) OPEN IN YOUR BROWSER")
