import * as d3 from "https://esm.sh/d3@7";

async function render({ model, el }) {
  const width = 800;
  const height = 700;
  const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/quartier_paris/exports/geojson";
  const response = await fetch(url);
  const data = await response.json();

  const svg = d3.select(el).append("svg")
    .attr("width", width).attr("height", height)
    .style("background", "transparent");

  const projection = d3.geoMercator().fitSize([width - 50, height - 150], data);
  const pathGenerator = d3.geoPath().projection(projection);

  const g = svg.append("g");
  const legendG = svg.append("g").attr("transform", `translate(${width/4}, ${height - 80})`);

  function updateMap() {
    const altitudes = model.get("altitude_data");
    const vals = Object.values(altitudes);
    const minAlt = Math.min(...vals) || 25;
    const maxAlt = Math.max(...vals) || 130;

    // Terrain scale: Brown/Beige for high, Blue/Green for low
    const colorScale = d3.scaleSequential(d3.interpolateWarm)
      .domain([minAlt, maxAlt]);

    g.selectAll("path")
      .data(data.features)
      .join("path")
      .attr("d", pathGenerator)
      .attr("class", "quartier-tile")
      .attr("fill", d => {
         // Matching by quartier name or code
         const alt = altitudes[d.properties.l_qu] || 35;
         return colorScale(alt);
      })
      .append("title")
      .text(d => `${d.properties.l_qu}: ~${altitudes[d.properties.l_qu] || "N/A"}m`);

    // Altitude Legend
    legendG.selectAll("*").remove();
    const legendWidth = width / 2;
    const legendScale = d3.scaleLinear().domain([minAlt, maxAlt]).range([0, legendWidth]);

    const defs = svg.append("defs");
    const gradient = defs.append("linearGradient").attr("id", "alt-gradient");
    gradient.selectAll("stop")
      .data(d3.range(0, 1.1, 0.1))
      .join("stop")
      .attr("offset", d => `${d*100}%`)
      .attr("stop-color", d => d3.interpolateWarm(d));

    legendG.append("rect").attr("width", legendWidth).attr("height", 15).style("fill", "url(#alt-gradient)");
    legendG.append("g").attr("transform", "translate(0,15)").call(d3.axisBottom(legendScale).ticks(5));
    legendG.append("text").attr("y", -10).attr("x", legendWidth/2).attr("text-anchor", "middle").text("Max Altitude (meters)");
  }

  model.on("change:altitude_data", updateMap);
  updateMap();
}
export default { render };
