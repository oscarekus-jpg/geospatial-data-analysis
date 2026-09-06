import duckdb

con_2 = duckdb.connect()
con_2.sql("INSTALL spatial; LOAD spatial;")

con_2.sql("INSTALL httpfs; LOAD httpfs")

power_url_2 = "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv"

# This query uses CTEs (WITH clauses), aggregations (SUM/COUNT), and spatial distance.
# 1 degree of latitude/longitude is roughly 111 km. 4.5 degrees is ~500km.

cloud_query_2 = f"""
    WITH target_city AS(
        SELECT ST_Point(19.9450, 50.0647) AS city_geom, 'Kraków' AS city_name
        ),
        regional_plants AS(
        SELECT
            name,
            primary_fuel,
            capacity_mw,
            ST_Point(longitude, latitude) AS plant_geom
        FROM '{power_url_2}'
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
    )
    
    SELECT
        p.primary_fuel AS energy_source,
        COUNT(p.name) AS number_of_plants,
        ROUND(SUM(p.capacity_mw), 2) AS total_megawatts
    FROM regional_plants p
    CROSS JOIN target_city t
    WHERE ST_Distance(p.plant_geom, t.city_geom) < 4.5
    GROUP BY p.primary_fuel
    ORDER BY total_megawatts DESC;
    """

df_regional_energy = con_2.sql(cloud_query_2).df()
print(df_regional_energy)

#creating a second query that lets mesave the loc to a file on my computer so I can have it as a layer.

# 2. EXPORT: Save the actual map points to a local file
print("\nExporting regional power plant geometries to GeoJSON...")

export_query = f"""
    COPY (
        WITH target_city AS (
            SELECT ST_Point(19.9450, 50.0647) AS city_geom
        )
        SELECT 
            name,
            primary_fuel,
            capacity_mw,
            ST_Point(longitude, latitude) AS geom
        FROM '{power_url_2}'
        CROSS JOIN target_city t
        WHERE ST_Distance(ST_Point(longitude, latitude), t.city_geom) < 4.5
    ) TO 'krakow_regional_plants.geojson' 
    WITH (FORMAT GDAL, DRIVER 'GeoJSON');
"""

con_2.sql(export_query)
print("Export complete! Check your project folder for 'krakow_regional_plants.geojson'.")