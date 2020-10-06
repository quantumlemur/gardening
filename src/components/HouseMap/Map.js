import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useSpring, animated } from "react-spring";
import { scaleLinear, scaleOrdinal, scaleTime } from "d3-scale";
import { extent } from "d3-array";
import { schemeCategory10, timeFormat, timeParse } from "d3";

import { Box, Heading, Text } from "gestalt";

function circleFill(d) {
  const calibrated_value = (d.value - d.calibration_min) / (d.calibration_max - d.calibration_min);
  return calibrated_value > .8 ? "red" : "green";
}

function Map({devices, activeDevice}) {
  const [data, setData] = useState(devices);

  function printData(event) {
    this.forceUpdate()
    console.log(data)
  }

  const props = useSpring({
    from: { r: 0 },
    to: { r: 10 }
  });

  const width = 640,
    height = 400

  const circles = data.map((d, i) => (
    <animated.circle
      key={i}
      r={props.r}
      cx={d.location_x}
      cy={d.location_y}
      style={{ fill: circleFill(d) }}
    />
  ));

  return (
    <div
      onClick={printData}
      style={{background: "color url('zone0.png')"}}>
      <svg width={width} height={height}>
        <image href="zone0.png" x="0" y="0" width={width} height={height}/>
        <g>
          {circles}
        </g>
      </svg>
    </div>
  );
}

export default Map;
