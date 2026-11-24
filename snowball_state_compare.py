
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

plotdatas = [
    "sbe_ocean_temp",
    "sbe_ocean_temp_and_ice",
    "sbe_mpiom_temp-ice_echam-ice-snow_jsbach_snow"
]

# Shorter titles for the plots
plot_titles = [
    "MPIOM temperature",
    "MPIOM temperature & seaice",
    "MPIOM temp & seaice, ECHAM seaice & snow, JSBACH snow"
]

data_dir = "data/"
output_dir = "plots/"

os.makedirs(output_dir, exist_ok=True)

show_YN = False

# All maps use identical colour scales
temperature_limit = 100
temperature_levels = np.linspace(-temperature_limit, temperature_limit, 25)
ice_levels = np.linspace(0, 1, 21)

# -1 selects the final available time step
time_index = -1


# --------------------------------------------------
# Load all experiments
# --------------------------------------------------

datasets = {}

for plotdata in plotdatas:

    spatial_path = data_dir + plotdata + "_echam6_BOT_annual_spatial_mean.nc"
    global_path = data_dir + plotdata + "_echam6_BOT_annual_global_mean.nc"

    ds_spatial = xr.open_dataset(spatial_path)
    ds_global = xr.open_dataset(global_path)

    # Spatial fields
    temperature = ds_spatial["tsurf"].isel(time=time_index) - 273.15
    seaice = ds_spatial["seaice"].isel(time=time_index)

    # Global mean temperature
    global_temperature = ds_global["tsurf"].squeeze() - 273.15

    # Time axes
    spatial_year = float(ds_spatial["time"].values[time_index]) / 1e4
    global_time = ds_global["time"].values / 1e4

    datasets[plotdata] = {
        "temperature": temperature,
        "seaice": seaice,
        "global_temperature": global_temperature,
        "time": global_time,
        "year": spatial_year
    }

    print(f"{plotdata}: final year {spatial_year:.0f}, temperature range {float(temperature.min()):.1f} to {float(temperature.max()):.1f} °C")

    ds_spatial.close()
    ds_global.close()


# --------------------------------------------------
# Create comparison figure
# --------------------------------------------------

fig = plt.figure(figsize=(17, 11))

gs = fig.add_gridspec(3, 4, height_ratios=[1, 1, 0.9], width_ratios=[1, 1, 1, 0.045], hspace=0.35, wspace=0.12)

temperature_axes = []
ice_axes = []


# --------------------------------------------------
# 1. Surface temperature maps
# --------------------------------------------------

for i, (plotdata, title) in enumerate(zip(plotdatas, plot_titles)):

    ax = fig.add_subplot(gs[0, i], projection=ccrs.Robinson())

    temperature = datasets[plotdata]["temperature"]

    im_temp = temperature.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="RdBu_r", levels=temperature_levels, add_colorbar=False)

    ax.set_global()
    ax.coastlines(linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)

    ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.4, color="gray", alpha=0.5, linestyle="--")

    year = datasets[plotdata]["year"]

    ax.set_title(f"{year:.0f}\n{title}", fontsize=11)

    temperature_axes.append(ax)


# Temperature colourbar on the right
cax_temp = fig.add_subplot(gs[0, 3])
cbar_temp = fig.colorbar(im_temp, cax=cax_temp, orientation="vertical", shrink=0.75)
cbar_temp.set_label(r"Surface temperature [$^\circ$C]", fontsize=10)


# --------------------------------------------------
# 2. Sea-ice maps
# --------------------------------------------------

for i, (plotdata, title) in enumerate(zip(plotdatas, plot_titles)):

    ax = fig.add_subplot(gs[1, i], projection=ccrs.Robinson())

    seaice = datasets[plotdata]["seaice"]

    im_ice = seaice.plot(ax=ax, transform=ccrs.PlateCarree(), cmap="Blues", levels=ice_levels, vmin=0, vmax=1, add_colorbar=False)

    ax.set_global()
    ax.coastlines(linewidth=0.6)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)

    ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.4, color="gray", alpha=0.5, linestyle="--")

    ax.set_title(f"{year:.0f}\n{title}", fontsize=11)

    ice_axes.append(ax)


# Sea-ice colourbar on the right
cax_ice = fig.add_subplot(gs[1, 3])
cbar_ice = fig.colorbar(im_ice, cax=cax_ice, orientation="vertical", shrink=0.75)
cbar_ice.set_label("Sea ice fraction", fontsize=10)


# --------------------------------------------------
# 3. Global mean temperature versus time
# --------------------------------------------------

ax = fig.add_subplot(gs[2, :])

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

for i, (plotdata, title) in enumerate(zip(plotdatas, plot_titles)):

    time = datasets[plotdata]["time"]
    temperature = datasets[plotdata]["global_temperature"]

    ax.plot(time, temperature.values, linewidth=1.6, color=f"C{i}", label=title)


ax.set_xlabel("Time [yr]")
ax.set_ylabel(r"Temperature [$^\circ$C]")
ax.set_title("Global mean surface temperature", fontsize=13)
ax.grid(True, alpha=0.3, linestyle="--")
ax.legend(loc="best", fontsize=9)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))


# --------------------------------------------------
# Overall layout and save
# --------------------------------------------------

plt.tight_layout()
fig.suptitle("Comparison of Snowball Earth simulations", fontsize=16, y=0.98)

fig.savefig(output_dir + "snowball_state_comparison.png", dpi=300, bbox_inches="tight")

print("Saved:", output_dir + "snowball_state_comparison.png")

if show_YN:
    plt.show()
else:
    plt.close(fig)

print("All plots completed.")
