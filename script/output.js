const showResult = (outputData) => {
    download("result.csv", outputData.map((row) => row.join(",")).join("\n"));
    plot(outputData);
};

const download = (filename, text) => {
    var pom = document.createElement("a");
    pom.setAttribute("href", "data:text/plain;charset=utf-8," + encodeURIComponent(text));
    pom.setAttribute("download", filename);

    if (document.createEvent) {
        var event = document.createEvent("MouseEvents");
        event.initEvent("click", true, true);
        pom.dispatchEvent(event);
    } else {
        pom.click();
    }
};

const initChart = (chartId) => {
    let target_width = document.getElementById(chartId).clientWidth;

    let margin = { top: 10, right: 30, bottom: 30, left: 60 };
    let width = target_width - margin.left - margin.right;
    let height = target_width - margin.top - margin.bottom;

    let svg = d3
        .select("#" + chartId)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        //.style("background-color", "lightblue")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    return { svg, width, height };
};

const draw = (ID, OD, svg, width, height) => {
    const [minX, maxX] = d3.extent(ID, (d) => d[0]);
    const [minY, maxY] = d3.extent(ID, (d) => d[1]);

    // Add X axis
    var x = d3.scaleLinear().domain([minX, maxX]).range([0, width]);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear().domain([minY, maxY]).range([height, 0]);
    svg.append("g").call(d3.axisLeft(y));

    // Add dots
    svg.append("g")
        .selectAll("dot")
        .data(ID)
        .enter()
        .append("circle")
        .attr("cx", function (d) {
            return x(d[0]);
        })
        .attr("cy", function (d) {
            return y(d[1]);
        })
        .attr("r", 2.0)
        .style("fill", "#69b3a2");

    // Add dots
    svg.append("g")
        .selectAll("dot")
        .data(OD)
        .enter()
        .append("circle")
        .attr("cx", function (d) {
            return x(d[0]);
        })
        .attr("cy", function (d) {
            return y(d[1]);
        })
        .attr("r", 4.0)
        .style("fill", "#B3697A");
};

const plot = (outputData) => {
    let OD = outputData.map((x) => [x[0], x[1]].map((y) => +y));
    let ID = inputData.map((x) => [x[0], x[1]].map((y) => +y));

    let { svg, width, height } = initChart("plot");
    draw(ID, OD, svg, width, height);
};
