import { scaleLinear } from "d3-scale";

import React from "react";

function AxisLeft({ xScale, yScale, width }) {
  const axis = yScale.ticks(5).map((d, i) => (
    <g key={i} className="y-tick">
      <line
        style={{ stroke: "#e4e5eb" }}
        strokeWidth={2}
        y1={yScale(d)}
        y2={yScale(d)}
        x1={xScale.range()[0]}
        x2={xScale.range()[0] * 0.75}
      />
      <text
        style={{ fontSize: 14, textAnchor: "end" }}
        x={width * 0.75}
        dy=".32em"
        y={yScale(d)}
      >
        {d}
      </text>
    </g>
  ));
  return <>{axis}</>;
}

export default AxisLeft;
