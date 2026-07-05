# r.hydro.hbv.forcing

## NAME

**r.hydro.hbv.forcing** - Reduces a gridded climate space-time raster
dataset (ERA5/ERA5-Land, MODIS, or any other daily raster time series)
to a per-basin daily long-format DB table for
*[r.hydro.hbv](r.hydro.hbv.md)*'s `*_table=` options.

## SYNOPSIS

**r.hydro.hbv.forcing**\
**r.hydro.hbv.forcing --help**\
**r.hydro.hbv.forcing** **strds**=*name* **basins**=*name*
**basins_vector**=*name* [**basin_id_column**=*name*]
**output_table**=*name*

## DESCRIPTION

*r.hydro.hbv.forcing* turns a daily raster time series (a space-time
raster dataset, STRDS -- e.g. an ERA5-Land precipitation or temperature
series already imported with *t.rast.import*, or any other daily
raster series registered into a STRDS) into the long-format
(`station_id`, `date`, `value`) DB table that
*[r.hydro.hbv](r.hydro.hbv.md)*'s `precipitation_table=`/
`temperature_table=`/etc. options expect, via one *t.rast.univar*
zonal-mean call against a *[r.hydro.hbv.basins](r.hydro.hbv.basins.md)*-
delineated basins raster.

**basins** is the delineated basins raster (`r.hydro.hbv.basins`'
`basins=` output); **basins_vector** is its vectorized counterpart
(`basins_vector=` output), used only to look up each basin's
**basin_id_column** value (default `basin_id`) so the output table's
`station_id` matches what `r.hydro.hbv` (or `r.hydro.hbv.basins`
itself) already uses.

## EXAMPLE

```sh
# basins already delineated by r.hydro.hbv.basins as basins/basins_v
t.create output=era5_precip type=strds temporaltype=absolute \
  title="ERA5-Land precipitation" description="..."
t.register input=era5_precip maps=`g.list type=raster pattern="era5_precip_*" separator=,` \
  start="2001-01-01" increment="1 days"

r.hydro.hbv.forcing strds=era5_precip basins=basins basins_vector=basins_v \
  output_table=era5_precip_table

r.hydro.hbv dataset=custom precipitation_table=era5_precip_table \
  temperature=temp.csv evapotranspiration=evap.csv eta_observed=etobs.csv \
  discharge_observed=dischargeobs.csv basins_vector=basins_v \
  n_calib_steps=1000 n_years=3 warmup=100 n_realizations=1000 \
  output=/tmp/hbv_era5
```

## SEE ALSO

*[r.hydro.hbv](r.hydro.hbv.md)*, *[r.hydro.hbv.basins](r.hydro.hbv.basins.md)*,
*[t.rast.univar](t.rast.univar.md)*, *[t.rast.import](t.rast.import.md)*,
*[t.create](t.create.md)*, *[t.register](t.register.md)*

## AUTHOR

Yann Chemin
