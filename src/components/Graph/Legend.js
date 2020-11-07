import React, { useEffect, useState, useRef } from "react";

import { scaleLinear } from "d3-scale";

// LegendData format:
// legendData = [
//   {
//     key: 1,
//     text: "first item",
//   },
//   {
//     key: 5,
//     text: "another item",
//   },
// ];
function Legend({ legendData, handleClick, colorScale }) {
  const [height, setHeight] = useState(0);
  const [width, setWidth] = useState(0);

  const ref = useRef(null);

  useEffect(() => {
    setHeight(ref.current.clientHeight);
    setWidth(ref.current.clientWidth);
  });

  const margin = {
    top: 0.05,
    bottom: 0.08,
    left: 0.1,
    right: 0.05,
  };

  const coords = {
    x: {
      left: width * margin.left,
      right: width * (1 - margin.right),
    },
    y: {
      bottom: height * (1 - margin.bottom),
      top: height * margin.top,
    },
  };

  // var legendItems = data.reduce(
  //   (accumulator, currentValue, currentIndex, sourceArray) =>
  //     accumulator.includes(
  //       [currentValue.device_id, currentValue.name].join("||")
  //     )
  //       ? accumulator
  //       : accumulator.concat(
  //           [currentValue.device_id, currentValue.name].join("||")
  //         ),
  //   []
  // );

  const yScale = scaleLinear()
    .domain([0, legendData.length])
    .range([coords.y.bottom, coords.y.top]);

  const labels = legendData.map((d, i) => (
    <g
      key={d.key}
      transform={`translate(0,${yScale(i)})`}
      onClick={() => handleClick(d)}
    >
      <circle r="10" fill={colorScale(d.key)} />
      <text x="20" fontSize="12">
        {d.text}
      </text>
    </g>
  ));

  return (
    <svg width="100%" height="auto" ref={ref}>
      <g transform={`translate(${coords.x.left},0)`}>{labels}</g>
    </svg>
  );
}

export default Legend;
