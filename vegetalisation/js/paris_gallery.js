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
