import React from "react";

import { timeFormat } from "d3";


function AxisBottom({ xScale, height }) {
  const textPadding = 10;

  var formatTime = timeFormat("%a %e");

  const axis = xScale.ticks().map((d, i) => (
    <g className="x-tick" key={i}>
      <line
        style={{ stroke: "#e4e5eb" }}
        y1={0}
        y2={height}
        x1={xScale(d)}
        x2={xScale(d)}
      />
      <text
        style={{ textAnchor: "middle", fontSize: 12 }}
        dy=".71em"
        x={xScale(d)}
        y={height + textPadding}
      >
        {formatTime(d*1000)}
      </text>

    </g>
  ));
  return <>{axis}</>;
}

export default AxisBottom;
