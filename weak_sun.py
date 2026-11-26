
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
import cmocean as cmo


# --------------------------------------------------
# Settings
# --------------------------------------------------

output_dir = "plots/"
show_YN = False

temperature_limit = 22  
temperature_levels = np.linspace(-temperature_limit, temperature_limit, temperature_limit*2+1)
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

global_recovery_files = {}
spatial_recovery_files = {}

for file in glob.glob(os.path.join("data/*.nc")):
    filename = os.path.basename(file)

    match_global = re.match(r"recovery-(\d+)-sun_echam6_BOT_annual_global_mean\.nc$", filename)
    match_spatial = re.match(r"recovery-(\d+)-sun_echam6_BOT_annual_spatial_mean\.nc$", filename)

    if match_global:
        global_recovery_files[int(match_global.group(1))] = file

    elif match_spatial:
        spatial_recovery_files[int(match_spatial.group(1))] = file

solar_values = sorted(set(global_files) & set(spatial_files))

if not solar_values:
    raise FileNotFoundError("No matching global and spatial NetCDF file pairs found.")

print("Found experiments:", solar_values)

# --------------------------------------------------
# Load data
# --------------------------------------------------
# flip order
solar_values = solar_values[::-1]

global_datasets = {}
spatial_datasets = {}
global_recovery_datasets = {}
spatial_recovery_datasets = {}

for solar in solar_values:
    global_datasets[solar] = xr.open_dataset(global_files[solar])
    spatial_datasets[solar] = xr.open_dataset(spatial_files[solar])
    global_recovery_datasets[solar] = xr.open_dataset(global_recovery_files[solar])
    spatial_recovery_datasets[solar] = xr.open_dataset(spatial_recovery_files[solar])

# --------------------------------------------------
# Extract variables
# --------------------------------------------------

temperature_maps = {}
ice_maps = {}
global_temperatures = {}
simulation_years = {}

temperature_maps_recovery = {}
ice_maps_recovery  = {}
global_temperatures_recovery  = {}
simulation_years_recovery  = {}


for solar in solar_values:

    ds_global = global_datasets[solar]
    ds_spatial = spatial_datasets[solar]

    ds_global_recovery = global_recovery_datasets[solar]
    ds_spatial_recovery = spatial_recovery_datasets[solar]

    temperature_maps[solar] = ds_spatial["tsurf"].isel(time=-1) - 273.15
    ice_maps[solar] = ds_spatial["seaice"].isel(time=-1)
    global_temperatures[solar] = (ds_global["tsurf"] - 273.15).squeeze()
    simulation_years[solar] = int((ds_spatial["time"].values[-1] - ds_spatial["time"].values[0])/ 1e4) + 1

    temperature_maps_recovery[solar] = ds_spatial_recovery["tsurf"].isel(time=-1) - 273.15
    ice_maps_recovery[solar] = ds_spatial_recovery["seaice"].isel(time=-1)
    global_temperatures_recovery[solar] = (ds_global_recovery["tsurf"] - 273.15).squeeze()
    simulation_years_recovery[solar] = int((ds_spatial_recovery["time"].values[-1] - ds_spatial_recovery["time"].values[0])/ 1e4) + 1


# --------------------------------------------------
# Function for map plots
# --------------------------------------------------

    def plot_maps(data_dict, cmap, levels, title, bar_title, filename):

        n = len(data_dict)
        ncols = min(n, 2)
        nrows = int(np.ceil(n / ncols))
        
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3 * nrows), subplot_kw={"projection": ccrs.Robinson()}, squeeze=False)

        axes = axes.flatten()

        ims = []
        for ax, (solar, variable) in zip(axes, data_dict.items()):

            im = variable.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap, levels=levels, add_colorbar=False, zorder=1)       
            ims.append(im)

            ax.set_global()

            if cmap == cmo.cm.ice: 
                ax.add_feature(cfeature.LAND, facecolor="lightgrey", edgecolor="none", zorder=2)

            ax.coastlines(linewidth=0.7, zorder=3)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3, zorder=3)
                

            ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")

            ax.set_title(f"{solar}% solar forcing after {simulation_years[solar]} years", fontsize=12)

        for ax in axes[n:]:
            fig.delaxes(ax)

        fig.subplots_adjust(right=0.88, wspace=0.05, hspace=0.01)

        cbar_ax = fig.add_axes([0.91, 0.25, 0.02, 0.4])
        cbar = fig.colorbar(ims[0], cax=cbar_ax, orientation="vertical")
        cbar.set_label(bar_title, fontsize=11)

        fig.suptitle(title, fontsize=15)
        #plt.tight_layout()
        plt.savefig(output_dir + filename, dpi=300, bbox_inches="tight")
        print("saved " + filename)

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
          filename="solarforcing_temperature_comparison.png")
"""
plot_maps(temperature_maps_recovery, cmap="RdBu_r", 
          levels=temperature_levels, 
          title="Surface recovery temperature from different solar forcings", 
          bar_title=r"Temperature [$^\circ$C]", 
          filename="solarforcing_recovery_temperature_comparison.png")
"""
# --------------------------------------------------
# 2. Sea ice maps
# --------------------------------------------------

plot_maps(ice_maps, 
          cmap=cmo.cm.ice, 
          levels=ice_levels, 
          title="Sea ice cover under different solar forcings", 
          bar_title="Sea ice fraction", 
          filename="solarforcing_sea_ice_comparison.png")
"""
plot_maps(ice_maps_recovery, 
          cmap=cmo.cm.ice, 
          levels=ice_levels, 
          title="Sea ice cover recovery from different solar forcings", 
          bar_title="Sea ice fraction", 
          filename="solarforcing_recovery_sea_ice_comparison.png")
"""
# --------------------------------------------------
# 3. Global mean temperature versus time
# --------------------------------------------------

# Get first data point
ds_control = xr.open_dataset("data/piControl-CR-course_echam6_BOT_20yr_global_mean.nc")
control_temperature = (ds_control["tsurf"].squeeze().item() - 273.15)

fig, ax = plt.subplots(figsize=(6, 4))
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

for i, solar in enumerate(solar_values):

    ds = global_datasets[solar]
    time = ds["time"].values / 1e4
    T_global = global_temperatures[solar]
    T_global = np.insert(T_global, 0, control_temperature, axis=0)
    time = np.insert(time, 0, 1850, axis=0)
    
    overlap_year = 1880

    ds_recovery = global_recovery_datasets[solar]
    time_recovery = ds_recovery["time"].values / 1e4 + 30
    T_global_recovery = global_temperatures_recovery[solar]
    T_global_recovery = np.insert(T_global_recovery, 0, T_global.values[overlap_year-1850], axis=0)
    time_recovery = np.insert(time_recovery, 0, time[overlap_year-1850], axis=0)
 
    ax.plot(time, T_global.values, color=f"C{i}", label=f"{solar}%")
    ax.plot(time_recovery, T_global_recovery.values, color=f"C{i}", linestyle="--" )


ax.set_xlabel("Time [yr]")
ax.set_ylabel(r"Temperature [$^\circ$C]")
ax.set_title("Global mean surface temperature")
ax.grid(True, alpha=0.3, linestyle="--")
ax.legend(title="Solar forcing")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

plt.tight_layout()
plt.savefig(output_dir + "solarforcing_global_temperature_comparison.png", dpi=300)

print("saved global_temperature_comparison.png")

if show_YN:
    plt.show()
else:
    plt.close(fig)

# --------------------------------------------------
# 4. Gregory plot: Net radiation versus temperature change
# --------------------------------------------------

# Control climate reference values
N_control = (ds_control["trad0"].squeeze().item()+ ds_control["srad0"].squeeze().item())

T_control = ds_control["tsurf"].squeeze().item()

fig, ax = plt.subplots(figsize=(7, 5))

for i, solar in enumerate(solar_values):

    ds = global_datasets[solar]

    # Net radiation imbalance
    N = (ds["trad0"] + ds["srad0"]).squeeze().values

    # Global mean surface temperature
    T = ds["tsurf"].squeeze().values

    # Changes relative to control climate
    delta_N = N - N_control
    delta_T = T - T_control

    # Remove invalid values
    valid = np.isfinite(delta_T) & np.isfinite(delta_N)
    delta_T = delta_T[valid]
    delta_N = delta_N[valid]

    # Linear regression
    slope, intercept = np.polyfit(delta_T, delta_N, 1)

    # Regression line
    T_fit = np.linspace(delta_T.min(), delta_T.max(), 100)
    N_fit = slope * T_fit + intercept

    # Scatter and regression
    ax.scatter(delta_T, delta_N, color=f"C{i}", label=f"{solar}% solar")

    ax.plot(T_fit, N_fit, color=f"C{i}", linestyle="--")

ax.axhline(0, color="black", linewidth=0.8, alpha=0.6, linestyle="--")
ax.axvline(0, color="black", linewidth=0.8, alpha=0.6, linestyle="--")

ax.set_xlabel(r"Temperature change, $\Delta T$ [K]")
ax.set_ylabel(r"Net radiation change, $\Delta N$ [W m$^{-2}$]")
ax.set_title("Gregory plot: Different solar forcings")

ax.grid(True, alpha=0.3, linestyle="--")
ax.legend(title="Solar forcing")

plt.tight_layout()
plt.savefig(output_dir + "solarforcing_gregory_comparison.png",
            dpi=300, bbox_inches="tight")

print("saved gregory_comparison.png")

# --------------------------------------------------
# Close datasets
# --------------------------------

print("All plots saved in:", output_dir)

