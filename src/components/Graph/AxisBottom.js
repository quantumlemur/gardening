import React from "react";

import { timeDay, timeWeek, timeFormat } from "d3";

function AxisBottom({ xScale, yScale }) {
  var dayFormat = timeFormat("%a %m/%d");
  var dateFormat = timeFormat("%a");

  const minorAxis = xScale.ticks(timeDay).map((d, i) => (
    <g className="x-tick" key={i}>
      <line
        style={{ stroke: "#e4e5eb77" }}
        strokeWidth={1}
        y1={yScale.range()[0]}
        y2={yScale.range()[1]}
        x1={xScale(d)}
        x2={xScale(d)}
      />
    </g>
  ));

  const majorAxis = xScale.ticks(timeWeek).map((d, i) => (
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
        {dayFormat(d)}
      </text>
    </g>
  ));
  return (
    <>
      {minorAxis}
      {majorAxis}
    </>
  );
}

export default AxisBottom;
