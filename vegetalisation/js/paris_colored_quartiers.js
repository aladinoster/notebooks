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
