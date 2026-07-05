# r.hydro.hbv.forcing

A [GRASS GIS](https://grass.osgeo.org/) addon that reduces a gridded
climate space-time raster dataset (ERA5/ERA5-Land, MODIS, or any other
daily raster time series) to a per-basin daily long-format DB table for
[r.hydro.hbv](https://github.com/YannChemin/r.hydro.hbv)'s `*_table=`
options — the bridge between a climate STRDS and the model's
per-station forcing input.

```
# basins already delineated by r.hydro.hbv.basins as basins/basins_v
r.hydro.hbv.forcing strds=era5_precip basins=basins basins_vector=basins_v \
  output_table=era5_precip_table

r.hydro.hbv dataset=custom precipitation_table=era5_precip_table \
  temperature=temp.csv evapotranspiration=evap.csv eta_observed=etobs.csv \
  discharge_observed=dischargeobs.csv basins_vector=basins_v \
  n_calib_steps=1000 n_years=3 warmup=100 n_realizations=1000 \
  output=/tmp/hbv_era5
```

## Why

`r.hydro.hbv` accepts precipitation/temperature/evapotranspiration as a
long-format (`station_id, date, value`) GRASS DB table instead of a
CSV — this module builds that table directly from a climate STRDS via
one `t.rast.univar` zonal-mean call against a basins raster, instead of
hand-writing per-timestep extraction code.

## How it works

`strds=` is any daily raster time series already imported and
registered (e.g. via
[t.in.era5](https://github.com/YannChemin/t.in.era5), or
`t.rast.import` from any other source). `basins=` is the delineated
basins raster from
[r.hydro.hbv.basins](https://github.com/YannChemin/r.hydro.hbv.basins)'
`basins=` output; `basins_vector=` is its vectorized counterpart, used
only to look up each basin's `basin_id_column` value (default
`basin_id`) so the output table's `station_id` matches what
`r.hydro.hbv`/`r.hydro.hbv.basins` already use.

One `t.rast.univar zones=<basins>` call computes the zonal mean for
every timestep in the STRDS at once; the result is written to
`output_table=` as `(station_id, date, value)` rows, ready to hand
straight to `r.hydro.hbv`'s `precipitation_table=`/`temperature_table=`/
`evapotranspiration_table=`/etc.

## Options

| Option | Description |
|---|---|
| `strds` | Input space-time raster dataset |
| `basins` | Delineated basins raster (`r.hydro.hbv.basins`' `basins=` output) |
| `basins_vector` | Its vectorized counterpart, for `station_id` lookup |
| `basin_id_column` | Column in `basins_vector` naming each basin (default `basin_id`) |
| `output_table` | Name for the resulting long-format DB table |

## Requirements

- GRASS GIS core: the temporal framework (`t.rast.univar`,
  `t.rast.import`, `t.create`, `t.register`)

## Install

```
g.extension extension=r.hydro.hbv.forcing url=https://github.com/YannChemin/r.hydro.hbv.forcing
```

## Testing

No standalone testsuite lives in this repo yet — it's exercised
end-to-end (built against a hand-built STRDS, then fed straight back
into `r.hydro.hbv`, asserting bit-for-bit identical output to an
equivalent CSV-based run) by `r.hydro.hbv`'s
`testsuite/test_table_io.py`.

## License

Public domain — see [LICENSE](LICENSE) (Unlicense).

## See also

- [r.hydro.hbv](https://github.com/YannChemin/r.hydro.hbv) — the HBV
  model this module's tables feed
- [r.hydro.hbv.basins](https://github.com/YannChemin/r.hydro.hbv.basins) —
  delineates the basins raster this module reduces a STRDS against
- [t.in.era5](https://github.com/YannChemin/t.in.era5) — fetches an
  ERA5(-Land) STRDS to feed this module, no account/API key beyond a
  free CDS login
