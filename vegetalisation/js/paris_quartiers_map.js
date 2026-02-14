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
