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
