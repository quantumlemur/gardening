import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useSpring, animated } from "react-spring";
import { scaleLinear, scaleOrdinal, scaleTime } from "d3-scale";
import { extent } from "d3-array";
import { schemeCategory10, timeFormat, timeParse } from "d3";

import { Box, Heading, Text } from "gestalt";



function Map({devices, activeDevice}) {
  const [data, setData] = useState(devices);


  function printData(event) {
    console.log(data)
  }

  const props = useSpring({
    from: { r: 0 },
    to: { r: 10 }
  });

  var colorScale = scaleLinear().domain([0,1])
  .range(["green", "brown"])

  const width = 640,
    height = 400

  const circles = data.map((d, i) => (
    <animated.circle
      key={i}
      r={props.r}
      cx={d.location_x}
      cy={d.location_y}
      fill={d.id == activeDevice.id ? "blue" : colorScale(d.calibrated_value)}
    />
  ));

  const now = new Date();
  const crosses = data.map((d, i) => (
    <polyline
      key={i}
      points={[
        d.location_x-10, d.location_y-10,
        d.location_x+10, d.location_y+10,
        d.location_x, d.location_y,
        d.location_x-10, d.location_y+10,
        d.location_x+10, d.location_y-10
      ].join(", ")}
      stroke="red"
      strokeWidth={now > d.device_next_init*1000 ? "5" : "0"}
      fill="none"
    />
  ));

  return (
    <div
      onClick={printData}
      style={{background: "color url('zone0.png')"}}>
      <svg width={width} height={height}>
        <image href="/zone0.png" x="0" y="0" width={width} height={height}/>
        <g>
          {circles}
          {crosses}
        </g>
      </svg>
    </div>
  );
}

export default Map;
