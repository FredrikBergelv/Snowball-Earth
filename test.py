import xarray as xr

ds = xr.open_dataset("data/sbe_mpiom_temp-ice_echam-ice-snow_jsbach_snow_echam6_BOT_annual_spatial_mean.nc")

print(ds.data_vars)

print(ds["sn"].attrs)
