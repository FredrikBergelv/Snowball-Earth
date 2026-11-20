
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
import cmocean.cm as cmo


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

    simulation_years[solar] = int((ds_spatial["time"].values[-1] - ds_spatial["time"].values[0])/ 1e4) + 1

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

            im = variable.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap, levels=levels, add_colorbar=False)       
            ims.append(im)

            ax.set_global()
            ax.coastlines(linewidth=0.7)
            ax.add_feature(cfeature.BORDERS, linewidth=0.3)

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

# Get first data point
ds_control = xr.open_dataset("data/piControl-CR-course_echam6_BOT_20yr_global_mean.nc")
control_temperature = (ds_control["tsurf"].squeeze().item() - 273.15)

fig, ax = plt.subplots(figsize=(6, 4))
ax.axhline(0, color="black", linewidth=0.8)

for i, solar in enumerate(solar_values):

    ds = global_datasets[solar]
    time = ds["time"].values / 1e4
    T_global = global_temperatures[solar]
    
    T_global = np.insert(T_global, 0, control_temperature, axis=0)
    time = np.insert(time, 0, 1850, axis=0)

    ax.plot(time, T_global.values, color=f"C{i}", label=f"{solar}%")

ax.set_xlabel("Time [yr]")
ax.set_ylabel(r"Temperature [$^\circ$C]")
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
# 4. Gregory plot: Net radiation imbalance vs temperature
# --------------------------------------------------

# Control reference values
N_ctrl = (
    ds_control["trad0"].squeeze().item()
    + ds_control["srad0"].squeeze().item()
)

T_ctrl = ds_control["tsurf"].squeeze().item()

print(f"\nControl radiation imbalance: {N_ctrl:.2f} W/m²")

fig, ax = plt.subplots(figsize=(7, 5))

gregory_results = {}

for i, solar in enumerate(solar_values):

    ds = global_datasets[solar]

    # Net radiation imbalance
    N = (ds["trad0"] + ds["srad0"]).squeeze().values
    del_N = N - N_ctrl

    # Global mean temperature change
    T = ds["tsurf"].squeeze().values
    del_T = T - T_ctrl

    # Remove any invalid values
    valid = np.isfinite(del_T) & np.isfinite(del_N)
    del_T = del_T[valid]
    del_N = del_N[valid]

    # Gregory regression
    coefficients, covariance = np.polyfit(del_T, del_N, 1, cov=True)

    k, m = coefficients
    sigma_k, sigma_m = np.sqrt(np.diag(covariance))

    # Equilibrium climate sensitivity
    ECS = -m / k

    sigma_ECS = np.sqrt(
        (m / k**2)**2 * covariance[0, 0]
        + (1 / k)**2 * covariance[1, 1]
        - 2 * m / k**3 * covariance[0, 1]
    )

    gregory_results[solar] = (k, m, ECS, sigma_ECS)

    print(f"\n{solar}% solar forcing:")
    print(f"Feedback parameter: {k:.2f} ± {sigma_k:.2f} W/m²/K")
    print(f"Intercept:          {m:.2f} ± {sigma_m:.2f} W/m²")
    print(f"ECS:                {ECS:.2f} ± {sigma_ECS:.2f} K")

    # Scatter points
    ax.scatter(
        del_T, del_N,
        color=f"C{i}",
        label=f"{solar}% solar forcing"
    )

    # Linear regression line
    x_fit = np.linspace(np.min(del_T), np.max(del_T), 200)

    ax.plot(
        x_fit,
        k * x_fit + m,
        color=f"C{i}",
        linestyle="--",
        label=f"Linear fit {solar}%"
    )

ax.set_xlabel(r"Temperature change, $\Delta T$ [K]", fontsize=12)
ax.set_ylabel(r"Radiation imbalance, $\Delta N$ [W/m$^2$]", fontsize=12)
ax.set_title("Gregory plot", fontsize=15)

ax.grid(True, linestyle="--", alpha=0.6)
ax.legend(fontsize=10)

plt.xlim(-40,0)
plt.ylim(-80,0)

plt.tight_layout()
plt.savefig(output_dir + "gregory_comparison.png", dpi=300)

if show_YN:
    plt.show()
else:
    plt.close(fig)


# --------------------------------------------------
# Close datasets
# --------------------------------

print("All plots saved in:", output_dir)

