import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useSpring, animated } from "react-spring";
import { scaleLinear, scaleOrdinal, scaleTime } from "d3-scale";
import { schemeCategory10, extent, line } from "d3";
import AxisLeft from "./AxisLeft";
import AxisBottom from "./AxisBottom";

import { Box, Heading, Text } from "gestalt";

function ScatterGraph({ width, height, data }) {
  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipText, setTooltipText] = useState([]);
  const [tooltipTransform, setTooltipTransform] = useState("translate(0,0)");
  const [tooltipProps, setTooltipProps, stopTooltipProps] = useSpring(() => ({
    opacity: 0,
  }));

  //   div.transition()
  //       .duration(200)
  //       .style("opacity", .9);
  //   div.html(formatTime(d.date) + "<br/>"  + d.close)
  //       .styl
  //       .style("top", (d3.event.pageY - 28) + "px");
  //   }
  // onMouseOut={
  //   div.transition()
  //       .duration(500)
  //       .style("opacity", 0);
  //   }
  const margin = {
    top: 40,
    bottom: 40,
    left: 40,
    right: 40,
  };

  const innerWidth = width - margin.right - margin.left;
  const innerHeight = height - margin.top - margin.bottom;

  var xScale = scaleTime()
    .domain(extent(data, (d) => d.timestamp))
    .range([0, innerWidth]);

  const yAxisScale = scaleLinear().domain([0, 1]).range([0, innerHeight]);

  var colorScale = scaleOrdinal(schemeCategory10);

  //   function mouseEnter(e, d) {
  //     console.log(e.nativeEvent.offsetX);
  //     console.log(d);
  //     const date = new Date();
  //     const dateString = date.toString();
  //     setTooltipText([d.name, dateString, d.value + " => " + d.calibrated_value]);
  //     setTooltipProps({ opacity: 1 });
  //     setTooltipTransform(
  //       "translate(" +
  //         xScale(d.timestamp) +
  //         ", " +
  //         yScale(d.calibrated_value) +
  //         ")"
  //     );
  //   }

  //   function mouseLeave(e, d) {
  //     console.log(e);
  //     console.log(d);
  //     setTooltipProps({ opacity: 0 });
  //   }

  //   const circles = data.map((d, i) => (
  //     <animated.circle
  //       key={i}
  //       r={5}
  //       cx={xScale(d.timestamp)}
  //       cy={yScale(d.calibrated_value)}
  //       fill={colorScale(d.device_id)}
  //       onMouseEnter={(e) => mouseEnter(e, d)}
  //     />
  //   ));

  const lineData = data.reduce((accumulator, currentValue) => {
    if (accumulator[currentValue.device_id] == null) {
      accumulator[currentValue.device_id] = [];
    }
    accumulator[currentValue.device_id].push([
      currentValue.timestamp,
      currentValue.calibrated_value,
    ]);
    return accumulator;
  }, []);

  const d3line = line();

  const lines = lineData.map((points, i) => {
    const yScale = scaleLinear()
      .range([0, innerHeight])
      .domain(extent(points, (d) => d[1]));
    const scaledPoints = points.map((d, i) => [xScale(d[0]), yScale(d[1])]);
    const pathLine = d3line(scaledPoints);
    return (
      <path
        key={i}
        d={pathLine}
        stroke={colorScale(i)}
        strokeWidth="3"
        className="line"
        fill="none"
      />
    );
  });

  return (
    <svg width={width} height={height}>
      <g transform={`translate(${margin.left},${margin.top})`}>
        <AxisLeft yScale={yAxisScale} width={innerWidth} />
        <AxisBottom xScale={xScale} height={innerHeight} />
        {lines}
        <text transform={tooltipTransform}>
          <tspan x="10" y="45">
            {tooltipText[0]}
          </tspan>
          <tspan x="10" y="70">
            {tooltipText[1]}
          </tspan>
          <tspan x="10" y="95">
            {tooltipText[2]}
          </tspan>
        </text>
      </g>
    </svg>
  );
}

export default ScatterGraph;
