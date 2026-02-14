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
