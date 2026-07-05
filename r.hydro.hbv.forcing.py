#!/usr/bin/env python3
############################################################################
#
# MODULE:       r.hydro.hbv.forcing
# AUTHOR:       Yann Chemin
# PURPOSE:      Reduces a gridded climate space-time raster dataset
#               (STRDS) -- e.g. an ERA5/ERA5-Land precipitation or
#               temperature series, or any other daily raster time
#               series -- to a per-basin daily long-format
#               (station_id, date, value) DB table, via zonal means
#               against a r.hydro.hbv.basins-delineated basins raster.
#               That table is then usable directly as
#               r.hydro.hbv's precipitation_table=/temperature_table=/
#               etc. inputs, instead of a hand-built CSV.
# COPYRIGHT:    (C) 2026 by Yann Chemin
#               Released into the public domain -- see LICENSE (Unlicense).
#
############################################################################

# %module
# % description: Reduces a climate STRDS (ERA5/ERA5-Land, MODIS, or any other daily raster time series) to a per-basin daily long-format (station_id,date,value) DB table for r.hydro.hbv's *_table= options.
# % keyword: temporal
# % keyword: hydrology
# % keyword: HBV
# %end
# %option G_OPT_STRDS_INPUT
# % key: strds
# % description: Daily raster time series (precipitation, temperature, ...)
# %end
# %option G_OPT_R_INPUT
# % key: basins
# % description: Delineated basins raster (r.hydro.hbv.basins' basins= output)
# %end
# %option G_OPT_V_INPUT
# % key: basins_vector
# % description: Delineated basins vector, for the basin_id attribute (r.hydro.hbv.basins' basins_vector= output)
# %end
# %option G_OPT_DB_COLUMN
# % key: basin_id_column
# % answer: basin_id
# % description: Column in basins_vector holding the basin identifier
# %end
# %option
# % key: output_table
# % type: string
# % key_desc: name
# % required: yes
# % description: Name for the output long-format (station_id,date,value) DB table
# %end

import atexit
import csv
import io
import sys

import grass.script as gs

TMP_FILES = []


def cleanup():
    for path in TMP_FILES:
        gs.try_remove(path)


def basin_id_map(basins_vector, basin_id_column):
    """Returns {category: basin_id} from the basins vector's attribute
    table."""
    rows = gs.read_command(
        "v.db.select",
        map=basins_vector,
        columns=["cat", basin_id_column],
        format="csv",
    ).strip()
    reader = csv.reader(io.StringIO(rows))
    next(reader)  # header
    return {int(cat): basin_id for cat, basin_id in reader}


def main():
    options, _flags = gs.parser()

    ids = basin_id_map(options["basins_vector"], options["basin_id_column"])

    stats = gs.read_command(
        "t.rast.univar",
        input=options["strds"],
        zones=options["basins"],
        format="csv",
    ).strip()
    reader = csv.DictReader(io.StringIO(stats))

    # OGR's CSV driver needs an actual .csv extension (and its .csvt
    # sidecar to share that basename) to recognize the file.
    tmp_stem = gs.tempfile()
    long_csv = tmp_stem + ".csv"
    long_csvt = tmp_stem + ".csvt"
    TMP_FILES.extend([long_csv, long_csvt])

    n_rows = 0
    with open(long_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["station_id", "date", "value"])
        for row in reader:
            zone = int(row["zone"])
            if zone not in ids:
                gs.warning(
                    "Zone %d in t.rast.univar output has no matching "
                    "basin in <%s> -- skipped"
                    % (zone, options["basins_vector"])
                )
                continue
            date = row["start"].split(" ")[0]  # "YYYY-MM-DD HH:MM:SS" -> date
            try:
                mean = float(row["mean"])
            except (KeyError, ValueError):
                # a zone with no valid (non-NULL) cells for this
                # timestep -- t.rast.univar leaves "mean" blank rather
                # than reporting 0, which a plain float() re-validates
                # here since db.in.ogr's CSV driver otherwise aborts
                # the whole import on the first such row instead of
                # just skipping it.
                gs.warning(
                    "Zone %d has no valid mean for %s -- skipped"
                    % (zone, date)
                )
                continue
            writer.writerow([ids[zone], date, mean])
            n_rows += 1

    with open(long_csvt, "w") as f:
        f.write("String,String,Real\n")

    if n_rows == 0:
        gs.fatal(
            "No rows produced -- check that %s overlaps the basins "
            "raster's region and category values" % options["strds"]
        )

    # output_table is a DB table, not a raster/vector map, so this
    # module has no automatic --overwrite flag of its own (G_parser only
    # adds one when a G_OPT_*_OUTPUT map option is present) -- always
    # overwrite an existing table of the same name instead.
    gs.run_command(
        "db.in.ogr",
        input=long_csv,
        output=options["output_table"],
        overwrite=True,
    )

    gs.message(
        "Wrote %d (station, date) rows to table <%s>"
        % (n_rows, options["output_table"])
    )


if __name__ == "__main__":
    atexit.register(cleanup)
    sys.exit(main())
