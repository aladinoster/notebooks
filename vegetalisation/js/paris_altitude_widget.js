import * as d3 from "https://esm.sh/d3@7";

async function render({ model, el }) {
  const width = 800;
  const height = 650;

  const url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson";
  const response = await fetch(url);
  const geoData = await response.json();

  const svg = d3.select(el).append("svg")
    .attr("width", width)
    .attr("height", height)
    .style("background", "transparent");

  const projection = d3.geoMercator().fitSize([width - 40, height - 120], geoData);
  const pathGenerator = d3.geoPath().projection(projection);

  svg.append("g")
    .selectAll("path")
    .data(geoData.features)
    .join("path")
    .attr("d", pathGenerator)
    .style("fill", "#fdfdfd")
    .style("stroke", "#d1d1d1")
    .style("stroke-width", "1.5px");

  const pointGroup = svg.append("g");

  function update() {
    const points = model.get("points");
    if (!points || points.length === 0) return;

    const alts = points.map(d => d.alt);
    const minAlt = Math.min(...alts);
    const maxAlt = Math.max(...alts);

    const colorScale = d3.scaleSequential(d3.interpolateSpectral).domain([maxAlt, minAlt]);

    pointGroup.selectAll("circle")
      .data(points)
      .join("circle")
      .attr("cx", d => projection([d.lon, d.lat])[0])
      .attr("cy", d => projection([d.lon, d.lat])[1])
      .attr("r", 4)
      .attr("fill", d => colorScale(d.alt))
      .attr("stroke", "#fff")
      .attr("stroke-width", 0.5)
      .append("title")
      .text(d => `Altitude: ${d.alt ? d.alt.toFixed(1) : 0}m`);
  }

  update();
  model.on("change:points", update);
}
export default { render };
