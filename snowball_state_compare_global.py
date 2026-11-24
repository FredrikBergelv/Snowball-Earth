
#!/usr/bin/env python3
"""
@author: Fredrik Bergelv
"""


import os
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# --------------------------------------------------
# Settings
# --------------------------------------------------

plotdatas = [
    "sbe_ocean_temp",
    "sbe_ocean_temp_and_ice",
    "sbe_mpiom_temp-ice_echam-ice-snow_jsbach_snow"
]

plot_titles = [
    "MPIOM temperature",
    "MPIOM temperature & seaice",
    "MPIOM temp & seaice, ECHAM seaice & snow, JSBACH snow"
]

data_dir = "data/"
output_dir = "plots/"

os.makedirs(output_dir, exist_ok=True)

show_YN = False


# --------------------------------------------------
# Create plot
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 4))

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

for i, (plotdata, title) in enumerate(zip(plotdatas, plot_titles)):

    global_path = data_dir + plotdata + "_echam6_BOT_annual_global_mean.nc"

    ds_global = xr.open_dataset(global_path)

    temperature = ds_global["tsurf"].squeeze() - 273.15
    time = ds_global["time"].values / 1e4

    ax.plot(time, temperature.values, linewidth=1.6, color=f"C{i}", label=title)

    print(f"{plotdata}: final temperature {float(temperature.values[-1]):.2f} °C")

    ds_global.close()


# --------------------------------------------------
# Formatting
# --------------------------------------------------

ax.set_xlabel("Time [yr]")
ax.set_ylabel(r"Temperature [$^\circ$C]")
ax.set_title("Global mean surface temperature", fontsize=13)
ax.grid(True, alpha=0.3, linestyle="--")
ax.legend(loc="lower left", fontsize=9)
ax.xaxis.set_major_locator(MaxNLocator(integer=True))
ax.set_ylim(-55, 1)

fig.tight_layout()


# --------------------------------------------------
# Save and show
# --------------------------------------------------

fig.savefig(output_dir + "snowball_global_temperature_comparison.png", dpi=300, bbox_inches="tight")

print("Saved:", output_dir + "snowball_global_temperature_comparison.png")

if show_YN:
    plt.show()
else:
    plt.close(fig)

print("All plots completed.")
