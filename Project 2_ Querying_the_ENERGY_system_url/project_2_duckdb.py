import pandas as pd
import duckdb

#connecting a database connection that lives in my computers RAM\
con = duckdb.connect()

#telling duckdb to pull the spatial GIS tools needed
con.sql("INSTALL spatial;")
con.sql("LOAD spatial;")

#doing a test query
test_query = """
SELECT ST_distance(
    ST_point(0,0),
    ST_point(3,4)
    ) AS calculated_distance;
"""
#executing the actual sql and putting it into a dataframe
test_results = con.sql(test_query).df()
print(test_results)

#Allowing duckdb to check the borwsers, read files through the internet
con.sql("INSTALL httpfs; LOAD httpfs;")

#Fetching the file
power_url = "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv"

#checking the data for column names:
sample_df = con.sql(f"SELECT * FROM ST_Read('{power_url}') LIMIT 1;").df()
print(sample_df.columns.tolist())

#doing the sql from the url! 
cloud_query = f"""
    SELECT 
        name AS plant_name,
        country_long AS country,
        primary_fuel AS energy_source,
        capacity_mw AS megawatts,
        ST_AsText(ST_Point(longitude, latitude)) AS geometry
    FROM '{power_url}'
    WHERE primary_fuel = 'Solar'
      AND longitude IS NOT NULL 
      AND latitude IS NOT NULL
    ORDER BY capacity_mw DESC
    LIMIT 5;
"""

df_power_plants = con.sql(cloud_query).df()
print(df_power_plants)

