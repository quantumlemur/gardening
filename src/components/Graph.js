import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useSpring, animated } from "react-spring";
import { scaleLinear, scaleOrdinal, scaleTime } from "d3-scale";
import { extent } from "d3-array";
import { schemeCategory10, timeFormat, timeParse } from "d3";
import AxisLeft from "./Graph/AxisLeft";
import AxisBottom from "./Graph/AxisBottom";
import Legend from "./Graph/Legend";


import { Box, Heading, Text } from "gestalt";


function Graph() {
  const [data, setData] = useState([]);
  const [legend, setLegend] = useState(false);
  const [open, toggle] = useState(false);
  const props = useSpring({
    from: { r: 0, fill: "lightblue" },
    to: { r: open ? 10 : 5, fill: open ? "purple" : "lightblue" }
  });

  useEffect(() => {
    fetch("/api/get_sensor_data")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setLegend(<Legend width={w/10} height={h} data={data} />)
      });
  }, []);

  const w = 1200,
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
    .domain([Date.now()/1000 - 60*60*24*14, Date.now()/1000])
    .range([ 0, width ])
    .nice()

  const yScale = scaleLinear()
    .domain([0, 1])
    .range([0, height]);

  var colorScale = scaleOrdinal(schemeCategory10)

  const circles = data.map((d, i) => (
    <animated.circle
      key={i}
      r={props.r}
      cx={xScale(d.timestamp)}
      cy={yScale(d.calibrated_value)}
      fill={colorScale(d.device_id)}
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
        {legend}
      </div>
    </Box>
  );
}

export default Graph;
