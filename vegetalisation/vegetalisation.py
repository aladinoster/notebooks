# /// script
# dependencies = [
#     "altair==6.0.0",
#     "anywidget==0.9.21",
#     "duckdb==1.4.4",
#     "marimo",
#     "polars==1.38.1",
#     "pyarrow==23.0.0",
#     "sqlglot==28.10.1",
#     "traitlets==5.14.3",
# ]
# requires-python = ">=3.12"
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Analyzing Data From Vegetalisation in Paris
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Getting Arrondissements
    One could trace each one of the countours for the Paris arrondissements from:

    - [Arrondissements](https://opendata.paris.fr/explore/dataset/arrondissements/export)
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        INSTALL spatial; INSTALL httpfs;
        LOAD spatial; LOAD httpfs;
        """
    )
    return


@app.cell(hide_code=True)
def _():
    import pathlib
    import anywidget
    import traitlets

    class D3BarChart(anywidget.AnyWidget):
        # Pass data from Python to JS
        data = traitlets.List([]).tag(sync=True)

        _esm = pathlib.Path(__file__).parent / "js" / "d3_bar_chart.js"

    # 2. Usage
    data = [
        {"letter": "A", "frequency": 0.08167},
        {"letter": "B", "frequency": 0.01492},
        {"letter": "C", "frequency": 0.02782},
        {"letter": "D", "frequency": 0.04253},
        {"letter": "E", "frequency": 0.12702},
    ]

    chart = D3BarChart(data=data)
    return anywidget, pathlib, traitlets


@app.cell(hide_code=True)
def tiles(anywidget, pathlib):
    class ParisGallery(anywidget.AnyWidget):
        _esm = pathlib.Path(__file__).parent / "js" / "paris_gallery.js"

    # Instantiate the widget
    ParisGallery()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let now trace all Paris arrondisements via D3
    """)
    return


@app.cell(hide_code=True)
def arrondissements(anywidget, pathlib):
    class ParisEnhancedMap(anywidget.AnyWidget):
        _esm = pathlib.Path(__file__).parent / "js" / "paris_enhanced_map.js"
        _css = pathlib.Path(__file__).parent / "js" / "paris_enhanced_map.css"

    # Run the widget
    ParisEnhancedMap()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Getting Quartiers
    We can then establish in some way the same kind of data via:

    - [quartiers](https://opendata.paris.fr/explore/dataset/quartier_paris/information/)
    """)
    return


@app.cell(hide_code=True)
def quartiers(anywidget, pathlib):
    class ParisQuartiersMap(anywidget.AnyWidget):
        _esm = pathlib.Path(__file__).parent / "js" / "paris_quartiers_map.js"
        _css = pathlib.Path(__file__).parent / "js" / "paris_quartiers_map.css"

    ParisQuartiersMap()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Or color via arrondissements:
    """)
    return


@app.cell(hide_code=True)
def colorquartier(anywidget, pathlib):
    class ParisColoredQuartiers(anywidget.AnyWidget):
        _esm = pathlib.Path(__file__).parent / "js" / "paris_colored_quartiers.js"
        _css = pathlib.Path(__file__).parent / "js" / "paris_colored_quartiers.css"

    ParisColoredQuartiers()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Agregating Data
    One of the principles that may touch on arrondissements is the plan of vegetalisation, based on :

    - [vegetalisation](https://opendata.paris.fr/explore/dataset/permis-de-vegetaliser/information/)

    We can aggregate the data per arrondissement
    """)
    return


@app.cell(hide_code=True)
def _():
    import polars as pl 

    # 1. Fetch the 'Permis de Végétaliser' data
    data_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/permis-de-vegetaliser/exports/csv"

    # Load the data - forcing the separator to semicolon as per Paris Data standards
    df = pl.read_csv(data_url, separator=";")

    # 2. Aggregation Logic
    green_counts = (
        df.filter(pl.col("rv_arrdt").is_not_null())
        .group_by("rv_arrdt")
        .len()
        .with_columns(
            pl.col("rv_arrdt").cast(pl.String).str.slice(-2).cast(pl.Int32).alias("ar_code")
        )
    )

    # Create the map for the widget
    permission_map = dict(zip(green_counts["ar_code"].to_list(), green_counts["len"].to_list()))

    print(f"Processed {len(permission_map)} arrondissements.")
    print(f"Top sample: {list(permission_map.items())[:3]}")
    return permission_map, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Putting the data into the map
    """)
    return


@app.cell(hide_code=True)
def vegetalisation(anywidget, pathlib, permission_map, traitlets):
    class ParisGreenAnalysis(anywidget.AnyWidget):
        permission_data = traitlets.Dict({}).tag(sync=True)

        _esm = pathlib.Path(__file__).parent / "js" / "paris_green_analysis.js"
        _css = pathlib.Path(__file__).parent / "js" / "paris_green_analysis.css"

    # Launch the widget with our Polars data
    analysis_widget = ParisGreenAnalysis(permission_data=permission_map)
    analysis_widget
    return


@app.cell(hide_code=True)
def _(anywidget, pathlib, traitlets):
    class ParisAltitudeMap(anywidget.AnyWidget):
        # This dictionary will hold {quartier_code: max_altitude}
        altitude_data = traitlets.Dict({}).tag(sync=True)

        _esm = pathlib.Path(__file__).parent / "js" / "paris_altitude_map.js"
        _css = pathlib.Path(__file__).parent / "js" / "paris_altitude_map.css"

    return


@app.cell
def _():
    geojson_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/quartier_paris/exports/geojson"
    return (geojson_url,)


@app.cell(hide_code=True)
def _(geojson_url, mo):
    quartiers = mo.sql(
        f"""
        SELECT 
            features.properties.l_qu AS name, 
            features.properties.c_qu AS code,    
            ST_GeomFromGeoJSON(features.geometry::JSON) AS geom
            FROM (
                SELECT unnest(features) AS features 
                FROM read_json_auto('{geojson_url}')
            );
        """,
        output=False
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Altitude in Paris
    The following is the altitude in paris, to get this we sample a set of points from the `asc` files in:

    - [Altitude](https://geoservices.ign.fr/rgealti)

    via the script `rgealti_analysis.py` via `uv run rgealti_analysis.py`
    """)
    return


@app.cell
def _(mo):
    altitude = mo.sql(
        f"""
        SELECT
            lon,
            lat,
            altitude_m as alt
        FROM read_csv_auto('sample_points.csv');
        """
    )
    return (altitude,)


@app.cell(hide_code=True)
def _(pl):
    import math

    class ParisDataValidator:
        """
        Validates and cleans Polars DataFrames for Paris anywidget visualizations.
        Ensures no NaNs, nulls, or out-of-bounds coordinates reach the JS layer.
        """

        @staticmethod
        def clean_for_map(df: pl.DataFrame, lon_col="lon", lat_col="lat", alt_col="alt"):
            # 1. Cast to correct types and drop literal nulls
            cleaned = df.select([
                pl.col(lon_col).cast(pl.Float64),
                pl.col(lat_col).cast(pl.Float64),
                pl.col(alt_col).cast(pl.Float64)
            ]).drop_nulls()

            # 2. Filter out coordinates clearly outside of Paris bounds
            # Paris is roughly Lat: 48.8-48.9, Lon: 2.2-2.5
            cleaned = cleaned.filter(
                (pl.col(lon_col).is_between(2.0, 2.6)) &
                (pl.col(lat_col).is_between(48.7, 49.0))
            )

            # 3. Handle the "Hidden Nulls" (NaN and Infinity)
            # These often survive .drop_nulls() but break JS .toFixed()
            cleaned = cleaned.filter(
                pl.col(alt_col).is_finite() & 
                pl.col(lon_col).is_finite() & 
                pl.col(lat_col).is_finite()
            )

            initial_count = len(df)
            final_count = len(cleaned)

            if final_count < initial_count:
                print(f"Validator: Removed {initial_count - final_count} invalid rows.")

            return cleaned.to_dicts()

    return (ParisDataValidator,)


@app.cell(hide_code=True)
def _(ParisDataValidator, altitude, anywidget, pathlib, traitlets):
    class ParisAltitudeWidget(anywidget.AnyWidget):
        points = traitlets.List([]).tag(sync=True)

        _esm = pathlib.Path(__file__).parent / "js" / "paris_altitude_widget.js"

    # 2. Initialize the instance (Defining 'altitude_map')
    altitude_map = ParisAltitudeWidget()

    # 3. Clean and Pass Data using your Validator
    # (Assuming 'df' is your Polars DataFrame with lon, lat, alt)
    validator = ParisDataValidator()
    valid_points = validator.clean_for_map(altitude)

    # Assign data to the defined name
    altitude_map.points = valid_points

    # 4. Display the widget
    altitude_map
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
