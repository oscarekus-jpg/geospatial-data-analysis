import pystac_client
import planetary_computer

#connecting to the STAC, "modifier" will let us in
STAC1 = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# creating a bounding box for Tatra Mountains 
tatra_box = [19.9, 49.2,20.1,49.3]

#using autumn 2025 data
autumn_timestamp = "2025-09-01/2025-11-30"

#doing a query to fetch the data
search = STAC1.search(
    collections=["sentinel-2-l2a"],
    bbox=tatra_box,
    datetime=autumn_timestamp,
    query={"eo:cloud_cover": {'lt': 10}} #filtering for max 10% cloud cov on the data
)

collected_search = search.item_collection() # this takes the query and runs it in the connected url

print(len(collected_search))

#checking the first satelite sample
first_sample = collected_search[0]
print(first_sample)
print(first_sample.datetime)
print(len(first_sample.assets))

#checking different assets in the sample (different bands)

asset_name = list(first_sample.assets.keys())
for name in asset_name[:19]:
    print(f" name: {name}")


import rioxarray as rx

red_band_url = first_sample.assets['B04'].href
nir_band_url = first_sample.assets['B08'].href

print(f'red link {red_band_url}')
print(f'nir link:{nir_band_url}')

#checking out the first link
red_band = rx.open_rasterio(red_band_url)
nir_band = rx.open_rasterio(nir_band_url)
#checking the pixels and bands
print(red_band.shape)

#I WILL CALCULATE THE NDVI VALUES< HOWEVER FIRST I NEED TO CHANGE THE DATA TO NOT WHOLE NUMBERS
red_band = red_band.astype("float32")
nir_band = nir_band.astype("float32")

ndvi = (nir_band - red_band)/(nir_band+red_band)
print(f"calculated ndvi value: {ndvi}")

#visualizing the data calculated/fetched and queried

import matplotlib.pyplot as plt

ndvi_cropped = ndvi[0, 4010:5430, 160:4830]

plt.figure(figsize=(10,10))

# used this to do the crop - plt.imshow(ndvi[0].values, cmap="RdYlGn", vmin=-0.1, vmax=0.8)

ndvi_cropped.plot(cmap="RdYlGn", vmin=0.1, vmax=0.5)

plt.title("Tatra Mountains NDVI - Fall 2025")
plt.axis("off") 
plt.show()

#exporting the data as a geotif

ndvi_cropped = "outputs/tatry_ndvi_cropped.tif"
ndvi_cropped.rio.to_raster(ndvi_cropped)

print("file saved as tif")