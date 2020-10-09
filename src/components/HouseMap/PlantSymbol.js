import React, { useState } from "react";
import { Box, Heading, Text } from "gestalt";

function Cross({ data, index }) {
  const now = new Date();
  return (
    <polyline
      key={index}
      points={[
        data.location_x - 10,
        data.location_y - 10,
        data.location_x + 10,
        data.location_y + 10,
        data.location_x,
        data.location_y,
        data.location_x - 10,
        data.location_y + 10,
        data.location_x + 10,
        data.location_y - 10,
      ].join(", ")}
      stroke="red"
      strokeWidth={now > data.device_next_init * 1000 ? "5" : "0"}
      fill="none"
    />
  );
}

function Circle({ data, index, color }) {
  return (
    <circle
      key={index}
      r={10}
      cx={data.location_x}
      cy={data.location_y}
      fill={color}
    />
  );
}

function PlantSymbol(props) {
  const { data, index, onClick } = props;
  // var colorScale = scaleLinear().domain([0, 1]).range(["green", "brown"]);

  const color = "blue";
  return (
    <g onClick={() => onClick(data)}>
      <Circle data={data} index={index} color={color} />
      <Cross data={data} index={index} />
    </g>
  );
}

export default PlantSymbol;
