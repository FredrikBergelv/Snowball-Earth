
#!/usr/bin/env python3
"""
@author: Fredrik Bergelv
"""

import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import MaxNLocator


# --------------------------------------------------
# Settings
# --------------------------------------------------

#plotdata = "sbe_ocean_temp"
#plotdata = "sbe_ocean_temp_and_ice"
plotdata = "sbe_mpiom_temp-ice_echam-ice-snow_jsbach_snow"

data_dir = "data/"
output_dir = "plots/"

show_YN = False

temperature_limit = 100
temperature_levels = np.linspace(-temperature_limit, temperature_limit, 25)

snow_limit = 2.4
snow_levels = np.linspace(0, snow_limit, 25)

ice_levels = np.linspace(0, 1, 21)


# --------------------------------------------------
# Open data
# --------------------------------------------------

spatial_data_path = (data_dir + plotdata +"_echam6_BOT_annual_spatial_mean.nc")
global_data_path = (data_dir + plotdata + "_echam6_BOT_annual_global_mean.nc")

ds_spatial = xr.open_dataset(spatial_data_path)
ds_global = xr.open_dataset(global_data_path)


# --------------------------------------------------
# Extract variables
# --------------------------------------------------

# The year spatial fields
ntime = 1849 -1850

temperature_map = ds_spatial["tsurf"].isel(time=ntime) - 273.15
ice_map = ds_spatial["seaice"].isel(time=ntime)
snow_map = ds_spatial["sn"].isel(time=ntime)
last_year = ds_spatial["time"].values[ntime]

# Global mean temperature time series
global_temperature = (ds_global["tsurf"].squeeze() - 273.15)

time = ds_global["time"].values / 1e4

# Simulation duration
simulation_years = int((ds_spatial["time"].values[-1]- ds_spatial["time"].values[0]) / 1e4) + 1



print("Simulation:", plotdata)
print("Simulation duration:", simulation_years, "years")
print("Final time step:", last_year)

print("Final surface temperature range:",float(temperature_map.min()),"to",float(temperature_map.max()),"°C")


# --------------------------------------------------
# 1. Final-year surface temperature map
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5),subplot_kw={"projection": ccrs.Robinson()})

im = temperature_map.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    levels=temperature_levels,
    add_colorbar=False
    )

ax.set_global()
ax.coastlines(linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)

ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")

cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.06, shrink=0.75)

cbar.set_label(r"Temperature [$^\circ$C]")

ax.set_title(f"Surface temperature {int(last_year/1e4)}",fontsize=14)
ax.text(0.5, -0.1, "MPIOM temperature & seaice, ECHAM seaice & snow, JSBACH snow", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_state_temperature.png"
plt.savefig(output_dir + savename, dpi=300, bbox_inches="tight")

print("Saved", savename)

if show_YN:
    plt.show()
else:
    plt.close(fig)


# --------------------------------------------------
# 2. Final-year sea-ice map
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5), subplot_kw={"projection": ccrs.Robinson()})

im = ice_map.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="Blues",
    levels=ice_levels,
    vmin=0,
    vmax=1,
    add_colorbar=False
    )

ax.set_global()
ax.coastlines(linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)

ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")

cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.06, shrink=0.75)

cbar.set_label("Sea ice fraction")

ax.set_title(f"Sea ice cover {int(last_year/1e4)}", fontsize=14)
ax.text(0.5, -0.1, "MPIOM temperature & seaice, ECHAM seaice & snow, JSBACH snow", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_state_sea_ice.png"
plt.savefig(output_dir + savename, dpi=300, bbox_inches="tight")

print("Saved", savename)

if show_YN:
    plt.show()
else:
    plt.close(fig)

# --------------------------------------------------
# 3. Final-year snow map
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 5), subplot_kw={"projection": ccrs.Robinson()})

im = snow_map.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap="PuBuGn",
    levels=snow_levels,
    vmin=0,
    vmax=snow_limit,
    add_colorbar=False
    )

ax.set_global()
ax.coastlines(linewidth=0.7)
ax.add_feature(cfeature.BORDERS, linewidth=0.3)

ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")

cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.06, shrink=0.75)

cbar.set_label("Depth [m]")

ax.set_title(f"Snow depth {int(last_year/1e4)}", fontsize=14)
ax.text(0.5, -0.1, "MPIOM temperature & seaice, ECHAM seaice & snow, JSBACH snow", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_state_snow.png"
plt.savefig(output_dir + savename, dpi=300, bbox_inches="tight")

print("Saved", savename)

if show_YN:
    plt.show()
else:
    plt.close(fig)


# --------------------------------------------------
# 4. Global mean temperature versus time
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 4))

ax.axhline(0, color="black", linewidth=0.8, linestyle="-")

ax.plot(time, global_temperature.values, color="C1", label=plotdata)

ax.set_xlabel("Time [yr]")
ax.set_ylabel(r"Temperature [$^\circ$C]")
ax.set_title("Global mean surface temperature")

ax.grid(True, alpha=0.3, linestyle="--")
ax.legend()

ax.xaxis.set_major_locator(MaxNLocator(integer=True))
plt.tight_layout()

savename = "snowball_state_global_temperature.png"
plt.savefig(output_dir + savename, dpi=300, bbox_inches="tight")

print("Saved", savename)

if show_YN:
    plt.show()
else:
    plt.close(fig)


# --------------------------------------------------
# Close datasets
# --------------------------------------------------

ds_spatial.close()
ds_global.close()

print("All plots saved in:", output_dir)

