
#!/usr/bin/env python3
"""
@author: Fredrik Bergelv
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import mypy.mapplot as mp

show_YN = False

# --------------------------------------------------
# Open NetCDF files
# --------------------------------------------------

ds_sun_GAM = xr.open_dataset(r'data/weak-sun_echam6_BOT_annual_global_mean.nc')
ds_sun_GSM = xr.open_dataset(r'data/weak-sun_echam6_BOT_annual_spatial_mean.nc')

# --------------------------------------------------
# Calculate simulation length
# --------------------------------------------------

year_end = ds_sun_GSM.time.values[-1]
year_start = ds_sun_GSM.time.values[0]
year = int((year_end - year_start) / 10000) + 1

# --------------------------------------------------
# 1. Temperature map
# --------------------------------------------------

T_sun_last = ds_sun_GSM["tsurf"].isel(time=-1)
temperature_s = T_sun_last - 273.15

limit = float(np.ceil(abs(temperature_s).max()))
limit = 15  

mp.xarray(temperature_s, 
          projection="robinson", 
          cmap="RdBu_r", 
          valuescale=int(limit * 2), 
          mapscale="110m", 
          clim=(-limit, limit), 
          bartitle=r"Temperature [$^\circ$C]", 
          title=f"Surface temperature after {year} years of 0.8S$_0$", 
          outputdir="plots/map_temperature_weak_sun.png", 
          show=show_YN)

# --------------------------------------------------
# 2. Sea ice cover map
# --------------------------------------------------

ice_last = ds_sun_GSM["seaice"].isel(time=-1)
mp.xarray(ice_last, 
          projection="robinson", 
          cmap="Blues", 
          valuescale=21, 
          mapscale="110m", 
          clim=(0, 1), 
          bartitle="Sea ice fraction", 
          title=f"Sea ice cover after {year} years of 0.8S$_0$", 
          outputdir="plots/map_ice_weak_sun.png", 
          show=show_YN)


# --------------------------------------------------
# 3. Snow cover map
# --------------------------------------------------

snow_last = ds_sun_GSM["snc"].isel(time=-1)
mp.xarray(snow_last, 
          projection="robinson", 
          cmap="Blues", 
          valuescale=21, 
          mapscale="110m", 
          clim=(0, 0.01), 
          bartitle="Snow cover fraction", 
          title=f"Snow cover after {year} years of 0.8S$_0$", 
          outputdir="plots/map_snow_weak_sun.png", 
          show=show_YN)


# --------------------------------------------------
# 4. Global mean temperature versus time
# --------------------------------------------------


T_global = (ds_sun_GAM["tsurf"] - 273.15).squeeze()
time = ds_sun_GAM["time"].values / 1e4

plt.figure(figsize=(6, 4))
plt.scatter(time, T_global.values)
plt.xlabel("Time [yr]")
plt.ylabel(r"Global mean surface temperature [$^\circ$C]")
plt.title("Global mean surface temperature under 0.8S$_0$")
plt.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("plots/global_temperature_weak_sun.png", dpi=300)


