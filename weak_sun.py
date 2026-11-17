
#!/usr/bin/env python3
"""
@author: Fredrik Bergelv
"""


import os
import glob
import re
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.ticker import MaxNLocator


# --------------------------------------------------
# Settings
# --------------------------------------------------


output_dir = "plots/"
show_YN = False

temperature_limit = 15
temperature_levels = np.linspace(-temperature_limit, temperature_limit, 31)
ice_levels = np.linspace(0, 1, 21)

# --------------------------------------------------
# Find and match files
# --------------------------------------------------

global_files = {}
spatial_files = {}

for file in glob.glob(os.path.join("data/*.nc")):
    filename = os.path.basename(file)

    match_global = re.match(r"(\d+)-sun_echam6_BOT_annual_global_mean\.nc$", filename)
    match_spatial = re.match(r"(\d+)-sun_echam6_BOT_annual_spatial_mean\.nc$", filename)

    if match_global:
        global_files[int(match_global.group(1))] = file

    elif match_spatial:
        spatial_files[int(match_spatial.group(1))] = file

solar_values = sorted(set(global_files) & set(spatial_files))

if not solar_values:
    raise FileNotFoundError("No matching global and spatial NetCDF file pairs found.")

print("Found experiments:", solar_values)

# --------------------------------------------------
# Load data
# --------------------------------------------------

global_datasets = {}
spatial_datasets = {}

for solar in solar_values:
    global_datasets[solar] = xr.open_dataset(global_files[solar])
    spatial_datasets[solar] = xr.open_dataset(spatial_files[solar])

# --------------------------------------------------
# Extract variables
# --------------------------------------------------

temperature_maps = {}
ice_maps = {}
global_temperatures = {}
simulation_years = {}

for solar in solar_values:

    ds_global = global_datasets[solar]
    ds_spatial = spatial_datasets[solar]

    temperature_maps[solar] = ds_spatial["tsurf"].isel(time=-1) - 273.15
    ice_maps[solar] = ds_spatial["seaice"].isel(time=-1)

    global_temperatures[solar] = (ds_global["tsurf"] - 273.15).squeeze()

    simulation_years[solar] = int((ds_spatial["time"].values[-1] - ds_spatial["time"].values[0])/ 1e4)

# --------------------------------------------------
# Function for map plots
# --------------------------------------------------

def plot_maps(data_dict, cmap, levels, title, bar_title, filename):

    n = len(data_dict)
    ncols = min(n, 3)
    nrows = int(np.ceil(n / ncols))
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3.5 * nrows), subplot_kw={"projection": ccrs.Robinson()}, squeeze=False)

    axes = axes.flatten()

    for ax, (solar, variable) in zip(axes, data_dict.items()):

        im = variable.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap, levels=levels, add_colorbar=False)

        ax.set_global()
        ax.coastlines(linewidth=0.7)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3)

        ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")

        ax.set_title(f"{solar}% solar forcing after {simulation_years[solar]} years", fontsize=12)

    for ax in axes[n:]:
        fig.delaxes(ax)

    cbar = fig.colorbar(im, ax=axes[:n].tolist(), orientation="vertical", pad=0.06, shrink=0.8)
    cbar.set_label(bar_title, fontsize=11)

    fig.suptitle(title, fontsize=15)
    plt.tight_layout()
    plt.savefig(output_dir + filename, dpi=300)

    if show_YN:
        plt.show()
    else:
        plt.close(fig)

# --------------------------------------------------
# 1. Temperature maps
# --------------------------------------------------

plot_maps(temperature_maps, cmap="RdBu_r", 
          levels=temperature_levels, 
          title="Surface temperature under different solar forcings", 
          bar_title=r"Temperature [$^\circ$C]", 
          filename="temperature_comparison.png")

# --------------------------------------------------
# 2. Sea ice maps
# --------------------------------------------------

plot_maps(ice_maps, 
          cmap="Blues", 
          levels=ice_levels, 
          title="Sea ice cover under different solar forcings", 
          bar_title="Sea ice fraction", 
          filename="sea_ice_comparison.png")

# --------------------------------------------------
# 3. Global mean temperature versus time
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(6, 4))

for i, solar in enumerate(solar_values):

    ds = global_datasets[solar]
    time = ds["time"].values / 1e4
    time = [int(x) for x in time]
    T_global = global_temperatures[solar]

    ax.scatter(time, T_global.values, color=f"C{i}", s=20, label=f"{solar}%")

ax.set_xlabel("Time [yr]")
ax.set_ylabel(r"Global mean surface temperature [$^\circ$C]")
ax.set_title("Global mean surface temperature")
ax.grid(True, alpha=0.3, linestyle="--")
ax.legend(title="Solar forcing")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

plt.tight_layout()
plt.savefig(output_dir + "global_temperature_comparison.png", dpi=300)

if show_YN:
    plt.show()
else:
    plt.close(fig)

# --------------------------------------------------
# Close datasets
# --------------------------------

print("All plots saved in:", output_dir)

