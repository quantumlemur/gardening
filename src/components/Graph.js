import React, { useState } from "react";
import "gestalt/dist/gestalt.css";
import { useSpring, animated } from "react-spring";
import { scaleLinear, scaleOrdinal, scaleTime } from "d3-scale";
import { extent } from "d3-array";
import { schemeCategory10, timeFormat, timeParse } from "d3";
import AxisLeft from "./Graph/AxisLeft";
import AxisBottom from "./Graph/AxisBottom";

import { Box, Heading, Text } from "gestalt";


function Graph() {
  const [data, setData] = useState([]);
  const [open, toggle] = useState(false);
  const props = useSpring({
    from: { r: 0, fill: "lightblue" },
    to: { r: open ? 10 : 5, fill: open ? "purple" : "lightblue" }
  });

  fetch("/api/get_sensor_data")
    .then((res) => res.json())
    .then((data) => {
      setData(data);
    });

  const w = 600,
    h = 600,
    margin = {
      top: 40,
      bottom: 40,
      left: 40,
      right: 40
    };

  const width = w - margin.right - margin.left,
    height = h - margin.top - margin.bottom;

  var xScale = scaleTime()
    .domain([Date.now() - 1000*60*60*24*7, Date.now()])
    .range([ 0, width ])
    .nice()

  const yScale = scaleLinear()
    .domain(extent(data, d => d.calibrated_value))
    .range([height, 0]);

  var colorScale = scaleOrdinal(schemeCategory10)

  var formatTime = timeFormat("%e %b");
  var parseTime = timeParse("%a, %d %b %Y %H:%M:%S GMT");

  const circles = data.map((d, i) => (
    <animated.circle
      key={i}
      r={props.r}
      cx={xScale(parseTime(d.timestamp))}
      cy={yScale(d.calibrated_value)}
      style={{ fill: colorScale(d.device_id) }}
    />
  ));

  return (
    <Box
      display="flex"
      color="gray"
      justifyContent="center"
      alignItems="center"
      width="100vw"
      height="100vh"
    >
      <div>
        <svg width={w} height={h}>
          <g transform={`translate(${margin.left},${margin.top})`}>
            <AxisLeft yScale={yScale} width={width} />
            <AxisBottom xScale={xScale} height={height} />
            {circles}
          </g>
        </svg>
      </div>
    </Box>
  );
}

export default Graph;
