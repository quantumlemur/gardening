import React, { useState, useEffect } from "react";
import { scaleLinear, scaleOrdinal } from "d3-scale";
import { extent, schemeCategory10 } from "d3";

import LineGraph from "../Graph/LineGraph";

import { Box, Button, Modal, Layer, Text } from "gestalt";

// Format data for graph display.
// Input: List of points from get_sensor_data
// Output: List of x/y pairs
function processData(data) {
  const yExtent = extent(data, (d) => d.value);

  const mappedData = data.map((d, i) => {
    return {
      x: new Date(d.timestamp * 1000),
      y: d.value,
    };
  });
  const xExtent = extent(mappedData, (d) => d.x);

  return { data: mappedData, xExtent: xExtent, yExtent: yExtent };
}

function StatusModal({ currDevice, onSettingsButtonClick, onDismiss }) {
  const [device, setDevice] = useState(currDevice);
  const [graphData, setGraphData] = useState([]);
  const [xExtent, setxExtent] = useState([]);
  const [yExtent, setyExtent] = useState([]);

  useEffect(() => {
    fetch(`/api/get_sensor_data/${device.id}/soil`)
      .then((response) => response.json())
      .then((device_data) => {
        addDeviceData(device_data);
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

  var colorScale = scaleOrdinal(schemeCategory10);

  return (
    <Layer>
      <Modal
        heading={device.name}
        accessibilityModalLabel={device.name}
        onDismiss={onDismiss}
        size="sm"
      >
        <Text align="center">Voltage: {device.volt}</Text>
        <Box
          display="flex"
          wrap
          width="100%"
          direction="column"
          paddingX={3}
          paddingY={3}
        >
          <Box flex="grow" width="100%" padding={3}>
            <LineGraph
              graphData={graphData}
              colorScale={colorScale}
              xExtent={xExtent}
              yExtent={yExtent}
              invert={true}
            />
          </Box>
          <Button
            onClick={onSettingsButtonClick}
            color="blue"
            paddingX={3}
            paddingY={3}
            text="Settings"
          />
        </Box>
      </Modal>
    </Layer>
  );
}

export default StatusModal;
