import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { scaleLinear } from "d3-scale";
import { extent } from "d3";

import LineGraph from "./Graph/LineGraph";
import Legend from "./Graph/Legend";

import { Box, Heading, Text } from "gestalt";

// Format data for graph display.
// Input: List of points from get_sensor_data
// Output: List of x/y pairs
function processData(data) {
  const xExtent = extent(data, (d) => d.timestamp);
  const yExtent = extent(data, (d) => d.value);

  const yScale = scaleLinear().domain(yExtent).range([1, 0]);

  const mappedData = data.map((d, i) => {
    return {
      x: d.timestamp,
      y: yScale(d.value),
    };
  });
  return { data: mappedData, xExtent: xExtent, yExtent: [1, 0] };
}

// Format data for legend display.
function processLegendData(devices) {
  return devices.map((d, i) => {
    return {
      key: d.id,
      text: d.name,
    };
  });
}

function Graph() {
  const [legendData, setLegendData] = useState([]);
  const [graphData, setGraphData] = useState([]);
  const [xExtent, setxExtent] = useState([]);
  const [yExtent, setyExtent] = useState([]);

  useEffect(() => {
    fetch("/api/get_devices")
      .then((response) => response.json())
      .then((devices) => {
        setLegendData(processLegendData(devices));

        devices.forEach((device) => {
          fetch(`/api/get_sensor_data/${device.id}/soil`)
            .then((response) => response.json())
            .then((device_data) => {
              addDeviceData(device_data);
            });
        });
      });
  }, []);

  function addDeviceData(device_data) {
    if (device_data.length > 0) {
      const mappedData = processData(device_data);

      setxExtent((xExtent) => extent(xExtent.concat(mappedData.xExtent)));
      setyExtent((yExtent) => extent(yExtent.concat(mappedData.yExtent)));
      setGraphData((graphData) =>
        graphData.concat([
          {
            key: device_data[0].device_id,
            data: mappedData.data,
          },
        ])
      );
    }
  }

  return (
    <Box display="flex" width="100%" maxHeight={800}>
      <Box flex="grow" width="90%">
        <LineGraph
          graphData={graphData}
          xExtent={xExtent}
          yExtent={yExtent}
          invert={true}
        />
      </Box>
      <Box flex="grow" width="10%">
        <Legend legendData={legendData} />
      </Box>
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
