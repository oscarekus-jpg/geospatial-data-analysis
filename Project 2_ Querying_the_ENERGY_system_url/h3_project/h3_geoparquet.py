import duckdb

con_3 = duckdb.connect()

con_3.sql("INSTALL spatial; LOAD spatial")
con_3.sql("INSTALL httpfs; LOAD httpfs")

#adding ubers h3 grid
con_3.sql("INSTALL h3 FROM community;")
con_3.sql("LOAD h3;")

#adding the fetcher url
power_url_3 = "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv"

h3_query_test= f"""
    SELECT
        name,
        primary_fuel,
        h3_latlng_to_cell(latitude, longitude, 4) AS h3_index
    FROM '{power_url_3}'
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    LIMIT 5;
""" 
#printing the result of the query
df_h3_test = con_3.sql(h3_query_test).df()
print(df_h3_test)

#calcualting the total MW for every hxagon on EARHT

h3_query_real = f"""
    WITH h3_plants AS (
            SELECT
                primary_fuel,
                capacity_mw,
                h3_latlng_to_cell(latitude, longitude, 4) AS h3_index
            FROM '{power_url_3}'
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            )
        SELECT
            h3_index,
            primary_fuel,
            COUNT(primary_fuel) AS number_of_plants,
            ROUND(SUM(capacity_mw), 2) AS total_megawatts
        FROM h3_plants
        GROUP BY h3_index, primary_fuel
        ORDER BY total_megawatts DESC
        LIMIT 10
"""

df_h3_real = con_3.sql(h3_query_real).df()
print(df_h3_real)

#now I will export this data into a parquet file (the cloud standard)

export_parquet_query = f"""
    COPY(
        WITH h3_plants AS (
            SELECT 
                primary_fuel,
                capacity_mw,
                h3_latlng_to_cell(latitude, longitude, 4) AS h3_index
            FROM '{power_url_3}'
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            )
        SELECT
            h3_index,
            primary_fuel,
            COUNT(primary_fuel) AS number_of_plants,
            ROUND(SUM(capacity_mw),2) AS total_megawatts
        FROM h3_plants
        GROUP BY h3_index, primary_fuel
        ) TO 'global_h3_energy_grid.parquet' (FORMAT PARQUET);
    """

con_3.sql(export_parquet_query)
print("parquet file saved HEHE :) ")
