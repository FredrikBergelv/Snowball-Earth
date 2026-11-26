
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
import cmocean as cmo

# --------------------------------------------------
# Settings
# --------------------------------------------------

#plotdata = "sbe_ocean_05_temp"
plotdata = "sbe_ocean_10_temp"
#plotdata = "sbe_ocean_15_temp"
#plotdata = "sbe_ocean_temp_and_ice"
#plotdata = "sbe_mpiom_temp-ice_echam-ice-snow_jsbach_snow"

data_dir = "data/"
output_dir = "plots/"

show_YN = False

temperature_limit = 100
temperature_levels = np.linspace(-temperature_limit, temperature_limit, 25)

snow_limit = 1.0
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
ax.text(0.5, -0.1, "MPIOM potential temperature", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_ocean_temperature.png"
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
    cmap=cmo.cm.ice,
    levels=ice_levels,
    vmin=0,
    vmax=1,
    zorder=1,   
    add_colorbar=False
    )

ax.set_global()
ax.coastlines(linewidth=0.7, zorder=3)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, zorder=3)
ax.add_feature(cfeature.LAND, facecolor="lightgrey", edgecolor="none", zorder=2)

ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")

cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.06, shrink=0.75)

cbar.set_label("Sea ice fraction")

ax.set_title(f"Sea ice cover {int(last_year/1e4)}", fontsize=14)
ax.text(0.5, -0.1, "MPIOM temperature & seaice, ECHAM seaice & snow, JSBACH snow", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_all_sea_ice.png"
ax.text(0.5, -0.1, "MPIOM potential temperature", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_ocean_sea_ice.png"
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
    cmap=cmo.cm.rain,
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
ax.text(0.5, -0.1, "MPIOM potential temperature", transform=ax.transAxes, ha="center", fontsize=9)

savename = "snowball_ocean_snow.png"
plt.savefig(output_dir + savename, dpi=300, bbox_inches="tight")

print("Saved", savename)

if show_YN:
    plt.show()
else:
    plt.close(fig)


# --------------------------------------------------
# 4. Global mean temperature and sea-ice extent versus time
# --------------------------------------------------

# Latitude coordinate
if "lat" in ds_spatial.coords:
    latitude = ds_spatial["lat"]
elif "latitude" in ds_spatial.coords:
    latitude = ds_spatial["latitude"]
else:
    raise ValueError("Could not find latitude coordinate")

# Identify grid cells with sea ice 
ice_present = ds_spatial["seaice"] > 0.95

# Find the ice edge closest to the equator in each hemisphere
spatial_dims = [dim for dim in ice_present.dims if dim != "time"]

northern_ice = latitude.where(ice_present & (latitude > 0)).min(dim=spatial_dims)
southern_ice = latitude.where(ice_present & (latitude < 0)).max(dim=spatial_dims)

# Sea-ice time coordinate
time_ice = ds_spatial["time"].values / 1e4

# Plot
fig, ax1 = plt.subplots(figsize=(6, 4))

# Global mean temperature (left axis)

ax1.set_xlabel("Time [yr]")
ax1.set_ylabel(r"Temperature [$^\circ$C]")
ax1.tick_params(axis="y")
ax1.set_ylim(min(global_temperature.values)-1, 0    )

# Sea-ice extent (right axis)
ax2 = ax1.twinx()

#Southern hemisphere: fill from -90° to southern ice edge
ax2.fill_between(time_ice, -90, southern_ice.values, color="C0", alpha=0.3)

# Northern hemisphere: fill from northern ice edge to +90°
ax2.fill_between(time_ice, northern_ice.values, 90, color="C0", alpha=0.3, label="Ice extent")

ax1.plot(time, global_temperature.values, color="C1", label="Global mean temperature")

ax2.set_ylabel("Extent [°latitude]")
ax2.axhline(0, linewidth=0.8, linestyle="--", color="C0")
ax1.axhline(0, linewidth=0.8, linestyle="--", color="C1")
ax2.set_ylim(-90, 90)

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

ax1.set_title("Global mean temperature and sea-ice extent")
ax1.grid(True, alpha=0.3, linestyle="--")
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
ax1.set_zorder(ax2.get_zorder() + 1)
ax1.patch.set_visible(False)

plt.tight_layout()

savename = "snowball_ocean_global_temperature_and_ice_extent.png"
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

