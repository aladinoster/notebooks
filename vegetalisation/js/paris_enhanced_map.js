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
