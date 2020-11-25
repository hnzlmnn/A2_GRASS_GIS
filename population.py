#!/usr/bin/env python3

import sys
import subprocess
import numpy as np
import grass.script as gscript
import grass.script.array as garray


def main():
    region = gscript.region()
    nsres = region["nsres"]
    ewres = region["ewres"]
    delta = 1
    size = (250, 250)
    if not size[0] - delta < ewres < size[0] + 1:
        raise ValueError(f"EW resolution not {size[0]}+-{delta}")
    if not size[1] - delta < nsres < size[1] + 1:
        raise ValueError(f"NS resolution not {size[1]}+-{delta}")
    # Create one vector feature to improve speed for calculations
    print("Preparing data...", flush=True)
    gscript.run_command(
        "v.buffer",
        input="motorways@PERMANENT",
        output=f"motorway",
        distance=0.001,
        overwrite=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    distances = {
        250: None,
        500: None,
        1000: None,
        2500: None,
        5000: None,
    }
    for i in distances.keys():
        print(f"Starting calculation for {i}m distance", flush=True)
        print("Creating buffer", flush=True)
        gscript.run_command(
            "v.buffer",
            input="motorway@PERMANENT",
            output=f"motorway_buf_{i}",
            distance=i,
            overwrite=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        gscript.run_command(
            "g.region",
            vector=f"motorway_buf_{i}",
            overwrite=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("Rasterizing buffer", flush=True)
        gscript.run_command(
            "v.to.rast",
            input=f"motorway_buf_{i}@PERMANENT",
            output=f"motorway_rast_{i}",
            use="val",
            overwrite=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("Counting population", flush=True)
        gscript.run_command(
            "r.stats.zonal",
            base=f"motorway_rast_{i}@PERMANENT",
            cover="GHS_POP_E2015_GLOBE_R2019A_54009_250_V1_0_18_3@PERMANENT",
            method="sum",
            output=f"pop_motorway_{i}",
            overwrite=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        a = garray.array(f"pop_motorway_{i}@PERMANENT")
        distances[i] = np.amax(a)
    print("Populations:")
    for i, pop in distances.items():
        if pop is None: continue
        print(f"{i}m\t {pop}")


if __name__ == '__main__':
    main()