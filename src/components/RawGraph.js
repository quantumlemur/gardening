import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { scaleOrdinal } from "d3-scale";
import { extent, schemeCategory10 } from "d3";

import LineGraph from "./Graph/LineGraph";
import Legend from "./Graph/Legend";

import { Box } from "gestalt";

// Format data for graph display.
// Input: List of points from get_sensor_data
// Output: List of x/y pairs
function processData(data) {
  const xExtent = extent(data, (d) => d.timestamp);
  const yExtent = extent(data, (d) => d.value);

  const mappedData = data.map((d, i) => {
    return {
      x: d.timestamp,
      y: d.value,
    };
  });
  return {
    data: mappedData,
    xExtent: xExtent,
    yExtent: yExtent,
  };
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

function RawGraph() {
  const [legendData, setLegendData] = useState([]);
  const [allGraphData, setAllGraphData] = useState([]);
  const [selectedGraphData, setSelectedGraphData] = useState([]);
  const [xExtent, setxExtent] = useState([]);
  const [yExtent, setyExtent] = useState([]);

  useEffect(() => {
    fetch("/api/get_devices")
      .then((response) => response.json())
      .then((devices) => {
        setLegendData(processLegendData(devices));

        devices.forEach((device) => {
          fetch(`/api/get_raw_sensor_data/${device.id}/soil`)
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
      setAllGraphData((allGraphData) =>
        allGraphData.concat([
          {
            key: device_data[0].device_id,
            data: mappedData.data,
            highlight: false,
          },
        ])
      );
      setSelectedGraphData((selectedGraphData) =>
        selectedGraphData.concat([
          {
            key: device_data[0].device_id,
            data: mappedData.data,
            highlight: false,
          },
        ])
      );
      // setLegendData((legendData) =>
      //   legendData.concat([
      //     {
      //       key: mappedData.key,
      //       text: mappedData.text,
      //     },
      //   ])
      // );
    }
  }

  // Toggles a data item in the selectedGraphData list
  const handleClick = (device) => {
    const key = device.key;
    var index = -1;
    // First check for removal
    selectedGraphData.some((d, i) => {
      if (d.key === key) {
        index = i;
        return true;
      } else {
        return false;
      }
    });
    // If you don't find it, add it back in
    if (index > -1) {
      setSelectedGraphData((selectedGraphData) => [
        ...selectedGraphData.slice(0, index),
        ...selectedGraphData.slice(index + 1),
      ]);
    } else {
      allGraphData.some((d, i) => {
        if (d.key === key) {
          setSelectedGraphData((selectedGraphData) =>
            selectedGraphData.concat(d)
          );
          return true;
        }
        return false;
      });
    }
  };

  var colorScale = scaleOrdinal(schemeCategory10).domain(
    legendData.map((d) => d.key)
  );

  return (
    <Box display="flex" width="100%" maxHeight={800}>
      <Box flex="grow" width="90%">
        <LineGraph
          graphData={selectedGraphData}
          colorScale={colorScale}
          xExtent={xExtent}
          yExtent={yExtent}
          invert={true}
        />
      </Box>
      <Box flex="grow" width="10%">
        <Legend
          legendData={legendData}
          handleClick={handleClick}
          colorScale={colorScale}
        />
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

export default RawGraph;
