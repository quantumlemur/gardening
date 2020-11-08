import React from "react";

function PlantShadow({ x, y, pulse, needCharge, alert }) {
  return (
    <g transform={`translate(${x}, ${y})`}>
      <circle r="40" fill="url(#shadow)" pointerEvents="none" />
    </g>
  );
}

export default PlantShadow;
