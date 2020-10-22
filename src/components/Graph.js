import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import LineGraph from "./Graph/LineGraph";
import Legend from "./Graph/Legend";

import { Box, Heading, Text } from "gestalt";

function Graph() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("/api/get_sensor_data")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        // setLegend(<Legend width={w/10} height={h} data={data} />)
      });
  }, []);

  const w = 1200,
    h = 600;

  return (
    <Box>
      <LineGraph width={w} height={h} data={data} />
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
    </Box>
  );
}

export default Graph;
