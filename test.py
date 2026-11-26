import xarray as xr
import numpy as np

data_dir = "data/"
datasets = [
    "sbe_ocean_temp",
    "sbe_ocean_temp_and_ice",
    "sbe_mpiom_temp-ice_echam-ice-snow_jsbach_snow",
]
kinds = {
    "spatial": "_echam6_BOT_annual_spatial_mean.nc",
    "global":  "_echam6_BOT_annual_global_mean.nc",
}

for plotdata in datasets:
    for kind, suffix in kinds.items():
        path = data_dir + plotdata + suffix
        print(f"\n=== {plotdata} | {kind} ===\n{path}")
        try:
            ds = xr.open_dataset(path, decode_times=False)
        except FileNotFoundError:
            print("  MISSING")
            continue
        for name, da in ds.data_vars.items():
            if not np.issubdtype(da.dtype, np.number) or name.endswith(("_bnds", "_bounds")):
                continue
            units = da.attrs.get("units", "unitless")
            print(f"  {name:15s} min = {float(da.min()):12.5g}  max = {float(da.max()):12.5g}  [{units}]  {da.attrs.get('long_name', '')}")
        ds.close()