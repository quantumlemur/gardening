import React from "react";

import { timeFormat } from "d3";

function AxisBottom({ xScale, yScale, height }) {
  const textPadding = 1;

  var formatTime = timeFormat("%e");
  console.log(yScale.range());

  const axis = xScale.ticks().map((d, i) => (
    <g className="x-tick" key={i}>
      <line
        style={{ stroke: "#e4e5eb" }}
        strokeWidth={2}
        y1={yScale.range()[0]}
        y2={yScale.range()[1]}
        x1={xScale(d)}
        x2={xScale(d)}
      />
      <text
        style={{
          textAnchor: "middle",
          fontSize: 14,
          alignmentBaseline: "hanging",
        }}
        dy=".71em"
        x={xScale(d)}
        y={Math.max(...yScale.range())}
      >
        {formatTime(d * 1000)}
      </text>
    </g>
  ));
  return <>{axis}</>;
}

export default AxisBottom;
