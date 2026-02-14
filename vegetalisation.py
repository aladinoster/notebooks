# /// script
# dependencies = [
#     "anywidget==0.9.21",
#     "marimo",
#     "polars==1.38.1",
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


@app.cell(hide_code=True)
def tiles(anywidget):
    class ParisGallery(anywidget.AnyWidget):
        _esm = """
        import * as d3 from "https://esm.sh/d3@7";

        async function render({ model, el }) {
          // Direct API link from the Paris Data export page
          const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson";
          const response = await fetch(url);
          const data = await response.json();

          // Setup a CSS grid container for the tiles
          const container = d3.select(el)
            .append("div")
            .style("display", "grid")
            .style("grid-template-columns", "repeat(auto-fill, minmax(130px, 1fr))")
            .style("gap", "15px")
            .style("padding", "20px")
            .style("background", "#f0f2f5");

          // Sort arrondissements 1 to 20
          const sortedFeatures = data.features.sort((a, b) => 
            parseInt(a.properties.c_ar) - parseInt(b.properties.c_ar)
          );

          sortedFeatures.forEach(feature => {
            const card = container.append("div")
              .style("background", "white")
              .style("border-radius", "12px")
              .style("box-shadow", "0 4px 6px rgba(0,0,0,0.1)")
              .style("padding", "10px")
              .style("text-align", "center")
              .style("transition", "transform 0.2s")
              .on("mouseover", function() { d3.select(this).style("transform", "translateY(-5px)"); })
              .on("mouseout", function() { d3.select(this).style("transform", "translateY(0)"); });

            const svg = card.append("svg")
              .attr("width", 110)
              .attr("height", 110);

            // Individual projection for EACH arrondissement
            const projection = d3.geoMercator().fitSize([100, 100], feature);
            const path = d3.geoPath().projection(projection);

            svg.append("path")
              .datum(feature)
              .attr("d", path)
              .attr("fill", "#5f9ea0")
              .attr("stroke", "#2f4f4f")
              .attr("stroke-width", 1.5)
              .attr("transform", "translate(5, 5)"); // Small offset for centering

            card.append("div")
              .style("margin-top", "8px")
              .style("font-weight", "bold")
              .style("font-size", "13px")
              .style("color", "#333")
              .text(feature.properties.l_ar); // e.g., "1er Ardt"
          });
        }
        export default { render };
        """

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
def arrondissements(anywidget):
    class ParisEnhancedMap(anywidget.AnyWidget):
        _esm = """
        import * as d3 from "https://esm.sh/d3@7";

        async function render({ model, el }) {
          const width = 800;
          const height = 600;

          // Fetch raw data from your specific Paris Data link
          const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson";
          const response = await fetch(url);
          const data = await response.json();

          const svg = d3.select(el)
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .style("background", "transparent"); // No background

          const projection = d3.geoMercator().fitSize([width - 40, height - 40], data);
          const pathGenerator = d3.geoPath().projection(projection);

          // Draw all arrondissements as individual path elements
          const g = svg.append("g").attr("class", "arrondissement-container");

          g.selectAll("path")
            .data(data.features)
            .join("path")
            .attr("d", pathGenerator)
            .attr("class", "arrondissement-contour");

          // Add labels using PT Sans
          svg.append("g")
            .attr("class", "label-container")
            .selectAll("text")
            .data(data.features)
            .join("text")
            .attr("transform", d => `translate(${pathGenerator.centroid(d)})`)
            .text(d => d.properties.c_ar);
        }
        export default { render };
        """

        _css = """
        /* Import PT Sans from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&display=swap');

        .arrondissement-contour {
          fill: none;
          stroke: #2c3e50; /* Deep slate color */
          stroke-width: 2.5px; /* Enhanced contour width via CSS */
          stroke-linejoin: round;
          stroke-linecap: round;
          transition: stroke-width 0.2s, stroke 0.2s;
        }

        .arrondissement-contour:hover {
          stroke: #e67e22; /* Highlight color */
          stroke-width: 4px;
          cursor: pointer;
        }

        .label-container text {
          font-family: 'PT Sans', sans-serif; /* Apply PT Sans */
          font-size: 14px;
          font-weight: 700;
          fill: #2c3e50;
          text-anchor: middle;
          pointer-events: none;
        }
        """

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
def quartiers(anywidget):
    class ParisQuartiersMap(anywidget.AnyWidget):
        _esm = """
        import * as d3 from "https://esm.sh/d3@7";

        async function render({ model, el }) {
          const width = 800;
          const height = 600;

          // 1. Fetch the Quartiers GeoJSON
          const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/quartier_paris/exports/geojson";
          const response = await fetch(url);
          const data = await response.json();

          const svg = d3.select(el)
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .style("background", "transparent");

          const projection = d3.geoMercator().fitSize([width - 40, height - 40], data);
          const pathGenerator = d3.geoPath().projection(projection);

          // 2. Draw the 80 individual Quartier tiles
          svg.append("g")
            .selectAll("path")
            .data(data.features)
            .join("path")
            .attr("d", pathGenerator)
            .attr("class", "quartier-tile")
            .append("title")
            .text(d => `${d.properties.l_qu} (${d.properties.c_ar}e)`);
        }
        export default { render };
        """

        _css = """
        @import url('https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&display=swap');

        .quartier-tile {
          fill: #f9f9f9;
          stroke: #444;
          stroke-width: 0.8px; /* Thinner lines for smaller subdivisions */
          transition: all 0.2s;
        }

        .quartier-tile:hover {
          fill: #e67e22;
          stroke-width: 2px;
          cursor: pointer;
        }
        """

    ParisQuartiersMap()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Or color via arrondissements:
    """)
    return


@app.cell(hide_code=True)
def colorquartier(anywidget):
    class ParisColoredQuartiers(anywidget.AnyWidget):
        _esm = """
        import * as d3 from "https://esm.sh/d3@7";

        async function render({ model, el }) {
          const width = 800;
          const height = 600;

          // 1. Fetch the Quartiers GeoJSON
          const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/quartier_paris/exports/geojson";
          const response = await fetch(url);
          const data = await response.json();

          const svg = d3.select(el)
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height])
            .style("background", "transparent");

          const projection = d3.geoMercator().fitSize([width - 40, height - 40], data);
          const pathGenerator = d3.geoPath().projection(projection);

          // 2. Create a Categorical Color Scale
          // We use schemeTableau10 or schemeSet3 for a wide variety of colors
          const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

          // 3. Draw the 80 individual Quartier tiles with colors
          svg.append("g")
            .selectAll("path")
            .data(data.features)
            .join("path")
            .attr("d", pathGenerator)
            .attr("class", "quartier-tile")
            // Color is determined by the Arrondissement Number (c_ar)
            .attr("fill", d => colorScale(d.properties.c_ar))
            .append("title")
            .text(d => `${d.properties.l_qu} (${d.properties.c_ar}e)`);

          // 4. Centroid Labels for Arrondissements (Optional but helpful)
          // Grouping features to find centers for labels
          const labelData = d3.groups(data.features, d => d.properties.c_ar);

          svg.append("g")
            .attr("class", "label-container")
            .selectAll("text")
            .data(labelData)
            .join("text")
            .attr("transform", ([c_ar, features]) => {
               // Simple centroid of the first quartier in the group as a placeholder
               return `translate(${pathGenerator.centroid(features[0])})`;
            })
            .text(([c_ar]) => c_ar);
        }
        export default { render };
        """

        _css = """
        @import url('https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&display=swap');

        .quartier-tile {
          stroke: #fff;
          stroke-width: 0.5px;
          fill-opacity: 0.8;
          transition: fill-opacity 0.2s, stroke-width 0.2s;
        }

        .quartier-tile:hover {
          fill-opacity: 1;
          stroke-width: 2px;
          stroke: #333;
          cursor: pointer;
        }

        .label-container text {
          font-family: 'PT Sans', sans-serif;
          font-size: 14px;
          font-weight: 700;
          fill: #333;
          text-anchor: middle;
          pointer-events: none;
          paint-order: stroke;
          stroke: #fff;
          stroke-width: 2px;
        }
        """

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
    return (permission_map,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Putting the data into the map
    """)
    return


@app.cell(hide_code=True)
def vegetalisation(anywidget, permission_map, traitlets):
    class ParisGreenAnalysis(anywidget.AnyWidget):
        permission_data = traitlets.Dict({}).tag(sync=True)

        _esm = """
        import * as d3 from "https://esm.sh/d3@7";

        async function render({ model, el }) {
          const width = 800;
          const height = 550; // Increased height for the color bar
          const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/quartier_paris/exports/geojson";
          const response = await fetch(url);
          const data = await response.json();

          const svg = d3.select(el).append("svg")
            .attr("width", width).attr("height", height)
            .style("background", "transparent");

          const projection = d3.geoMercator().fitSize([width - 40, height - 100], data);
          const pathGenerator = d3.geoPath().projection(projection);

          // Main container for the map
          const g = svg.append("g");

          // Color Bar container (Legend)
          const legendG = svg.append("g")
            .attr("transform", `translate(${width / 4}, ${height - 60})`);

          function updateMap() {
            const counts = model.get("permission_data");
            const vals = Object.values(counts);
            const maxVal = vals.length > 0 ? Math.max(...vals) : 1;

            const colorScale = d3.scaleSequential(d3.interpolateGreens).domain([0, maxVal]);

            // 1. Draw/Update the Tiles
            g.selectAll("path")
              .data(data.features)
              .join("path")
              .attr("d", pathGenerator)
              .attr("class", "quartier-tile")
              .attr("fill", d => colorScale(counts[parseInt(d.properties.c_ar)] || 0))
              .on("mouseover", function(event, d) {
                const count = counts[parseInt(d.properties.c_ar)] || 0;
                d3.select(this).classed("highlighted", true);
                // Dynamic text update (or simple browser title)
                d3.select(this).select("title").text(`${d.properties.l_qu}: ${count} permissions`);
              })
              .on("mouseout", function() {
                d3.select(this).classed("highlighted", false);
              })
              .append("title"); // Tooltip placeholder

            // 2. Build the Color Bar (Legend)
            legendG.selectAll("*").remove(); // Clear previous

            const legendWidth = width / 2;
            const legendHeight = 15;

            // Use a canvas or linear gradient for the bar
            const defs = svg.append("defs");
            const linearGradient = defs.append("linearGradient").attr("id", "green-gradient");

            linearGradient.selectAll("stop")
              .data(d3.range(0, 1.1, 0.1))
              .join("stop")
              .attr("offset", d => `${d * 100}%`)
              .attr("stop-color", d => d3.interpolateGreens(d));

            legendG.append("rect")
              .attr("width", legendWidth)
              .attr("height", legendHeight)
              .style("fill", "url(#green-gradient)")
              .style("stroke", "#ccc");

            const legendScale = d3.scaleLinear().domain([0, maxVal]).range([0, legendWidth]);
            const legendAxis = d3.axisBottom(legendScale).ticks(5);

            legendG.append("g")
              .attr("transform", `translate(0, ${legendHeight})`)
              .call(legendAxis)
              .style("font-family", "PT Sans");

            legendG.append("text")
              .attr("x", legendWidth / 2)
              .attr("y", -10)
              .attr("text-anchor", "middle")
              .style("font-family", "PT Sans")
              .style("font-size", "12px")
              .text("Green Permissions Count");
          }

          model.on("change:permission_data", updateMap);
          updateMap();
        }
        export default { render };
        """

        _css = """
        @import url('https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&display=swap');

        .quartier-tile {
          stroke: #fff;
          stroke-width: 0.5px;
          transition: all 0.2s;
        }

        .quartier-tile.highlighted {
          stroke: #2c3e50;
          stroke-width: 1 px;
          fill-opacity: 0.7;
          cursor: crosshair;
        }
        """

    # Launch the widget with our Polars data
    analysis_widget = ParisGreenAnalysis(permission_data=permission_map)
    analysis_widget
    return


@app.cell(hide_code=True)
def _():
    import anywidget
    import traitlets

    class D3BarChart(anywidget.AnyWidget):
        # Pass data from Python to JS
        data = traitlets.List([]).tag(sync=True)

        _esm = """
        import * as d3 from "https://esm.sh/d3@7";

        function render({ model, el }) {
          let container = document.createElement("div");
          el.appendChild(container);

          function updateChart() {
            const data = model.get("data");
            if (!data || data.length === 0) return;

            // 1. Setup Dimensions
            const width = 640;
            const height = 400;
            const marginTop = 30;
            const marginRight = 0;
            const marginBottom = 30;
            const marginLeft = 40;

            // Clear previous chart
            container.innerHTML = "";

            // 2. Scales
            const x = d3.scaleBand()
              .domain(data.map(d => d.letter))
              .range([marginLeft, width - marginRight])
              .padding(0.1);

            const y = d3.scaleLinear()
              .domain([0, d3.max(data, d => d.frequency)])
              .range([height - marginBottom, marginTop]);

            // 3. Create SVG
            const svg = d3.select(container)
              .append("svg")
              .attr("width", width)
              .attr("height", height)
              .attr("viewBox", [0, 0, width, height])
              .attr("style", "max-width: 100%; height: auto;");

            // 4. Bars
            svg.append("g")
              .attr("fill", "steelblue")
              .selectAll("rect")
              .data(data)
              .join("rect")
              .attr("x", d => x(d.letter))
              .attr("y", d => y(d.frequency))
              .attr("height", d => y(0) - y(d.frequency))
              .attr("width", x.bandwidth());

            // 5. Axes
            svg.append("g")
              .attr("transform", `translate(0,${height - marginBottom})`)
              .call(d3.axisBottom(x).tickSizeOuter(0));

            svg.append("g")
              .attr("transform", `translate(${marginLeft},0)`)
              .call(d3.axisLeft(y).ticks(null, "%"))
              .call(g => g.select(".domain").remove());
          }

          // Initial render and listen for data changes
          model.on("change:data", updateChart);
          updateChart();
        }
        export default { render };
        """

    # 2. Usage
    data = [
        {"letter": "A", "frequency": 0.08167},
        {"letter": "B", "frequency": 0.01492},
        {"letter": "C", "frequency": 0.02782},
        {"letter": "D", "frequency": 0.04253},
        {"letter": "E", "frequency": 0.12702},
    ]

    chart = D3BarChart(data=data)
    return anywidget, traitlets


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
