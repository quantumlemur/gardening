import React, { useEffect, useState, useRef } from "react";
import "gestalt/dist/gestalt.css";
import { scaleLinear, scaleTime } from "d3-scale";
import { line } from "d3";
import AxisLeft from "./AxisLeft";
import AxisBottom from "./AxisBottom";

// data input format: array of arrays of x/y pairs
// data will be colored according to the array index
// data = [
//   [
//     { x: 1, y: 1 },
//     { x: 2, y: 2 },
//   ],
//   [
//     { x: 1, y: 5 },
//     { x: 2, y: 6 },
//     { x: 3, y: 5 },
//   ],
// ];

function LineGraph({ graphData, colorScale, xExtent, yExtent, invert }) {
  const [height, setHeight] = useState(0);
  const [width, setWidth] = useState(0);

  // const [tooltipVisible, setTooltipVisible] = useState(false);
  // const [tooltipText, setTooltipText] = useState([]);
  // const [tooltipTransform, setTooltipTransform] = useState("translate(0,0)");
  // const [tooltipProps, setTooltipProps, stopTooltipProps] = useSpring(() => ({
  //   opacity: 0,
  // }));

  const ref = useRef(null);

  useEffect(() => {
    setHeight(ref.current.clientHeight);
    setWidth(ref.current.clientWidth);
  }, [setHeight, setWidth, ref]);

  //   div.transition()
  //       .duration(200)
  //       .style("opacity", .9);
  //   div.html(formatTime(d.date) + "<br/>"  + d.close)
  //       .styl
  //       .style("top", (d3.event.pageY - 28) + "px");
  //   }
  // onMouseOut={
  //   div.transition()
  //       .duration(500)
  //       .style("opacity", 0);
  //   }

  // margins as percentage of svg size
  const margin = {
    top: 10,
    bottom: 30,
    left: 40,
    right: 10,
  };

  const coords = {
    x: {
      left: margin.left,
      right: width - margin.right,
    },
    y: {
      bottom: height - margin.bottom,
      top: margin.top,
    },
  };

  // console.log(graphData);
  var xScale = scaleTime()
    .domain(xExtent)
    .range([coords.x.left, coords.x.right]);
  // .nice();

  const yScale = scaleLinear()
    .domain(yExtent)
    .range(
      invert ? [coords.y.top, coords.y.bottom] : [coords.y.bottom, coords.y.top]
    );

  //   function mouseEnter(e, d) {
  //     console.log(e.nativeEvent.offsetX);
  //     console.log(d);
  //     const date = new Date();
  //     const dateString = date.toString();
  //     setTooltipText([d.name, dateString, d.value + " => " + d.calibrated_value]);
  //     setTooltipProps({ opacity: 1 });
  //     setTooltipTransform(
  //       "translate(" +
  //         xScale(d.timestamp) +
  //         ", " +
  //         yScale(d.calibrated_value) +
  //         ")"
  //     );
  //   }

  //   function mouseLeave(e, d) {
  //     console.log(e);
  //     console.log(d);
  //     setTooltipProps({ opacity: 0 });
  //   }

  //   const circles = data.map((d, i) => (
  //     <animated.circle
  //       key={i}
  //       r={5}
  //       cx={xScale(d.timestamp)}
  //       cy={yScale(d.calibrated_value)}
  //       fill={colorScale(d.device_id)}
  //       onMouseEnter={(e) => mouseEnter(e, d)}
  //     />
  //   ));

  // const lineData = data.reduce((accumulator, currentValue) => {
  //   if (accumulator[currentValue.device_id] == null) {
  //     accumulator[currentValue.device_id] = [];
  //   }
  //   accumulator[currentValue.device_id].push([
  //     currentValue.timestamp,
  //     currentValue.value,
  //   ]);
  //   return accumulator;
  // }, []);

  const d3line = line();

  const lines = graphData.map((graphSeries, i) => {
    // const yScale = scaleLinear()
    //   .domain(extent(points, (d) => d.y))
    //   .range([coords.y.bottom, coords.y.top]);
    const scaledPoints = graphSeries.data.map((d, i) => [
      xScale(d.x),
      yScale(d.y),
    ]);
    const pathLine = d3line(scaledPoints);
    return (
      <path
        key={graphSeries.key}
        d={pathLine}
        stroke={colorScale(graphSeries.key)}
        strokeWidth={graphSeries.highlight ? "20" : "2"}
        className="line"
        fill="none"
      />
    );
  });

  return (
    <svg width="100%" height="auto" ref={ref}>
      <AxisBottom xScale={xScale} yScale={yScale} />
      <AxisLeft xScale={xScale} yScale={yScale} />
      {lines}
      {/* <text transform={tooltipTransform}>
        <tspan x="10" y="45">
          {tooltipText[0]}
        </tspan>
        <tspan x="10" y="70">
          {tooltipText[1]}
        </tspan>
        <tspan x="10" y="95">
          {tooltipText[2]}
        </tspan>
      </text> */}
    </svg>
  );
}

export default LineGraph;
