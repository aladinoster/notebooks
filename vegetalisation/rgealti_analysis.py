# /// script
# dependencies = [
#     "marimo",
#     "numpy",
#     "polars",
#     "pyproj",
#     "typer",
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # RGE ALTI - Paris Elevation Analysis

    Analyze IGN RGE ALTI 1m elevation tiles (`.asc`) for Paris (D075).
    Extracts per-tile statistics (min, max, mean altitude) and 10 random sample points,
    with coordinate conversion from Lambert 93 to WGS84.
    """)
    return


@app.cell
def _():
    import numpy as np
    import polars as pl
    from pyproj import Transformer
    from pathlib import Path
    import typer
    import marimo as mo
    return Path, Transformer, mo, np, pl, typer


@app.cell
def _(Path, mo, typer):
    _default_dir = str(
        Path.home()
        / "Downloads"
        / "RGEALTI_2-0_1M_ASC_LAMB93-IGN69_D075_2020-07-30"
        / "RGEALTI"
        / "1_DONNEES_LIVRAISON_2021-01-00157"
        / "RGEALTI_MNT_1M_ASC_LAMB93_IGN69_D075_20210118"
    )

    app = typer.Typer()

    @app.command()
    def main(
        data_dir: str = typer.Argument(default=_default_dir, help="Path to MNT .asc directory"),
    ):
        return data_dir

    args = mo.cli_args()
    data_directory = Path(args.get("data_dir", _default_dir) if args else _default_dir)

    mo.md(f"**Data directory:** `{data_directory}`")
    return data_directory,


@app.cell
def _(np):
    def parse_asc(filepath):
        """Parse an ESRI ASCII Grid file header and load elevation data."""
        header = {}
        with open(filepath, "r") as f:
            for _ in range(6):
                line = f.readline().split()
                header[line[0].lower()] = float(line[1])

        ncols = int(header["ncols"])
        nrows = int(header["nrows"])
        xll = header["xllcorner"]
        yll = header["yllcorner"]
        cellsize = header["cellsize"]
        nodata = header["nodata_value"]

        data = np.loadtxt(filepath, skiprows=6, dtype=np.float32)

        # Mask NODATA values
        valid_mask = data != nodata

        return {
            "ncols": ncols,
            "nrows": nrows,
            "xllcorner": xll,
            "yllcorner": yll,
            "cellsize": cellsize,
            "nodata": nodata,
            "data": data,
            "valid_mask": valid_mask,
        }
    return (parse_asc,)


@app.cell
def _(Transformer, data_directory, mo, np, parse_asc, pl):
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)

    asc_files = sorted(data_directory.glob("*.asc"))
    mo.md(f"Found **{len(asc_files)}** tiles to process.")

    tile_records = []
    sample_records = []
    rng = np.random.default_rng(seed=42)

    with mo.status.progress_bar(total=len(asc_files)) as bar:
        for fpath in asc_files:
            bar.update(title=fpath.name)

            parsed = parse_asc(fpath)
            data = parsed["data"]
            mask = parsed["valid_mask"]
            valid_data = data[mask]

            xll = parsed["xllcorner"]
            yll = parsed["yllcorner"]
            cs = parsed["cellsize"]
            ncols = parsed["ncols"]
            nrows = parsed["nrows"]

            # Bounding box in Lambert 93
            xmin = xll
            ymin = yll
            xmax = xll + ncols * cs
            ymax = yll + nrows * cs

            # Centroid in Lambert 93
            cx_l93 = (xmin + xmax) / 2
            cy_l93 = (ymin + ymax) / 2

            # Convert centroid to WGS84
            lon, lat = transformer.transform(cx_l93, cy_l93)

            tile_records.append({
                "file": fpath.name,
                "min_altitude_m": float(valid_data.min()),
                "max_altitude_m": float(valid_data.max()),
                "mean_altitude_m": float(valid_data.mean()),
                "centroid_x_l93": cx_l93,
                "centroid_y_l93": cy_l93,
                "centroid_lon": lon,
                "centroid_lat": lat,
                "xmin_l93": xmin,
                "ymin_l93": ymin,
                "xmax_l93": xmax,
                "ymax_l93": ymax,
                "valid_pixels": int(mask.sum()),
                "nodata_pixels": int((~mask).sum()),
            })

            # Sample 10 random valid points
            valid_indices = np.argwhere(mask)
            chosen = rng.choice(len(valid_indices), size=min(10, len(valid_indices)), replace=False)
            for idx in chosen:
                row, col = valid_indices[idx]
                # Pixel center coordinates in Lambert 93
                px_l93 = xll + (col + 0.5) * cs
                py_l93 = yll + (nrows - row - 0.5) * cs  # rows go top to bottom
                s_lon, s_lat = transformer.transform(px_l93, py_l93)
                sample_records.append({
                    "file": fpath.name,
                    "row": int(row),
                    "col": int(col),
                    "altitude_m": float(data[row, col]),
                    "x_l93": px_l93,
                    "y_l93": py_l93,
                    "lon": s_lon,
                    "lat": s_lat,
                    "is_sample": True,
                })

    df_tiles = pl.DataFrame(tile_records)
    df_samples = pl.DataFrame(sample_records)
    return df_samples, df_tiles


@app.cell(hide_code=True)
def _(df_tiles, mo):
    mo.md(r"""
    ## Tile Statistics

    Summary of elevation statistics per tile (MNT):
    """)
    mo.ui.table(df_tiles)
    return


@app.cell(hide_code=True)
def _(df_tiles, mo):
    summary = (
        f"- **Tiles processed:** {len(df_tiles)}\n"
        f"- **Global min altitude:** {df_tiles['min_altitude_m'].min():.2f} m\n"
        f"- **Global max altitude:** {df_tiles['max_altitude_m'].max():.2f} m\n"
        f"- **Global mean altitude:** {df_tiles['mean_altitude_m'].mean():.2f} m\n"
        f"- **Latitude range:** {df_tiles['centroid_lat'].min():.4f}° — {df_tiles['centroid_lat'].max():.4f}°\n"
        f"- **Longitude range:** {df_tiles['centroid_lon'].min():.4f}° — {df_tiles['centroid_lon'].max():.4f}°\n"
    )
    mo.md(f"## Global Summary\n\n{summary}")
    return


@app.cell(hide_code=True)
def _(df_samples, mo):
    mo.md(r"""
    ## Random Sample Points

    10 randomly sampled elevation points per tile:
    """)
    mo.ui.table(df_samples)
    return


@app.cell(hide_code=True)
def _(data_directory, df_samples, df_tiles, mo, pl):
    output_dir = data_directory.parent
    tiles_path = output_dir / "tile_statistics.csv"
    samples_path = output_dir / "sample_points.csv"

    df_tiles.write_csv(tiles_path)
    df_samples.write_csv(samples_path)

    # Combined export with is_sample flag
    df_tiles_export = df_tiles.with_columns(pl.lit(False).alias("is_sample"))
    df_combined = pl.concat(
        [
            df_tiles_export.select(
                "file", "mean_altitude_m", "centroid_x_l93", "centroid_y_l93",
                "centroid_lon", "centroid_lat", "is_sample",
            ).rename({"mean_altitude_m": "altitude_m", "centroid_x_l93": "x_l93",
                       "centroid_y_l93": "y_l93", "centroid_lon": "lon", "centroid_lat": "lat"}),
            df_samples.select("file", "altitude_m", "x_l93", "y_l93", "lon", "lat", "is_sample"),
        ],
        how="vertical",
    )
    combined_path = output_dir / "combined_output.csv"
    df_combined.write_csv(combined_path)

    mo.md(
        f"## Exported CSVs\n\n"
        f"- `{tiles_path}`\n"
        f"- `{samples_path}`\n"
        f"- `{combined_path}` (tiles + samples with `is_sample` flag)\n"
    )
    return


if __name__ == "__main__":
    app.run()
