import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useSpring, animated } from "react-spring";
import { scaleLinear, scaleOrdinal, scaleTime } from "d3-scale";
import { schemeCategory10, timeFormat, timeParse } from "d3";
import AxisLeft from "./Graph/AxisLeft";
import AxisBottom from "./Graph/AxisBottom";
import Legend from "./Graph/Legend";

import { Box, Heading, Text } from "gestalt";

function Graph() {
  const [data, setData] = useState([]);

  const [tooltipVisible, setTooltipVisible] = useState(false);
  const [tooltipText, setTooltipText] = useState([]);
  const [tooltipTransform, setTooltipTransform] = useState("translate(0,0)");
  const [tooltipProps, setTooltipProps, stopTooltipProps] = useSpring(() => ({
    opacity: 0,
  }));

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

  useEffect(() => {
    fetch("/api/get_sensor_data")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        // setLegend(<Legend width={w/10} height={h} data={data} />)
      });
  }, []);

  const w = 1200,
    h = 600,
    margin = {
      top: 40,
      bottom: 40,
      left: 40,
      right: 40,
    };

  const width = w - margin.right - margin.left,
    height = h - margin.top - margin.bottom;

  var xScale = scaleTime()
    .domain([Date.now() / 1000 - 60 * 60 * 24 * 14, Date.now() / 1000])
    .range([0, width])
    .nice();

  const yScale = scaleLinear().domain([0, 1]).range([0, height]);

  var colorScale = scaleOrdinal(schemeCategory10);

  function mouseEnter(e, d) {
    console.log(e.nativeEvent.offsetX);
    console.log(d);
    const date = new Date();
    const dateString = date.toString();
    setTooltipText([d.name, dateString, d.value + " => " + d.calibrated_value]);
    setTooltipProps({ opacity: 1 });
    setTooltipTransform(
      "translate(" +
        xScale(d.timestamp) +
        ", " +
        yScale(d.calibrated_value) +
        ")"
    );
  }

  function mouseLeave(e, d) {
    console.log(e);
    console.log(d);
    setTooltipProps({ opacity: 0 });
  }

  const circles = data.map((d, i) => (
    <animated.circle
      key={i}
      r={5}
      cx={xScale(d.timestamp)}
      cy={yScale(d.calibrated_value)}
      fill={colorScale(d.device_id)}
      onMouseEnter={(e) => mouseEnter(e, d)}
    />
  ));

  return (
    <Box>
      <div>
        <svg width={w} height={h}>
          <g transform={`translate(${margin.left},${margin.top})`}>
            <AxisLeft yScale={yScale} width={width} />
            <AxisBottom xScale={xScale} height={height} />
            {circles}
            <text transform={tooltipTransform}>
              <tspan x="10" y="45">
                {tooltipText[0]}
              </tspan>
              <tspan x="10" y="70">
                {tooltipText[1]}
              </tspan>
              <tspan x="10" y="95">
                {tooltipText[2]}
              </tspan>
            </text>
          </g>
        </svg>
        <Legend width={w / 10} height={h} data={data} />
        {/* <animated.div
          position="absolute"
          text-align="center"
          width="60px"
          height="28px"
          padding="2px"
          font="12px sans-serif"
          background="lightsteelblue"
          border="0px"
          border-radius="8px"
          style={tooltipProps}
        >
          {tooltipText}
        </animated.div> */}
      </div>
    </Box>
  );
}

export default Graph;
