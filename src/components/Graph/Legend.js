import React from "react";

import { schemeCategory10 } from "d3";
import { scaleLinear, scaleOrdinal } from "d3-scale";

function Legend({ width, height, data }) {
  const margin = {
    top: 40,
    bottom: 40,
    left: 10,
    right: 10,
  };

  var legendItems = data.reduce(
    (accumulator, currentValue, currentIndex, sourceArray) =>
      accumulator.includes(
        [currentValue.device_id, currentValue.name].join("||")
      )
        ? accumulator
        : accumulator.concat(
            [currentValue.device_id, currentValue.name].join("||")
          ),
    []
  );

  const yScale = scaleLinear()
    .domain([0, legendItems.length])
    .range([0, height - margin.top - margin.bottom]);

  var colorScale = scaleOrdinal(schemeCategory10);

  const labels = legendItems.map((d, i) => (
    <g key={i} transform={`translate(0, ${yScale(i)})`}>
      <circle r="10" fill={colorScale(d.split("||")[0])} />
      <text x="20" fontSize="12">
        {d.split("||")[1]}
      </text>
    </g>
  ));

  return (
    <svg width={width} height={height}>
      <g transform={`translate(${margin.left},${margin.top})`}>{labels}</g>
    </svg>
  );
}

export default Legend;
