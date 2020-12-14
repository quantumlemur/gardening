import React, { useState, useEffect } from "react";
import { scaleOrdinal } from "d3-scale";
import { extent, schemeCategory10 } from "d3";

import LineGraph from "../Graph/LineGraph";
import SettingsModal from "../ManageDevices/SettingsModal";

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

function calcBatteryStats(voltageData) {
  const endReading = voltageData[voltageData.length - 1];
  const targetTimestamp = endReading.timestamp - 60 * 60 * 24 * 3; // 3 days
  var startReading = {};
  voltageData.some((d) => {
    // get the first reading after the target timestamp
    if (d.timestamp > targetTimestamp) {
      startReading = d;
      return true;
    } else {
      return false;
    }
  });
  const tDelta =
    (endReading.timestamp - startReading.timestamp) / (60 * 60 * 24);
  const vDelta = startReading.value - endReading.value;

  const mvPerDay = vDelta / tDelta;
  const daysPerBattery = 800 / mvPerDay;
  return { mvPerDay: mvPerDay, daysPerBattery: daysPerBattery };
}

function StatusModal({ deviceId, onSettingsButtonClick, onDismiss }) {
  const [showSettings, setShowSettings] = useState(false);

  const [device, setDevice] = useState({});
  const [graphData, setGraphData] = useState([]);
  const [xExtent, setxExtent] = useState([]);
  const [yExtent, setyExtent] = useState([]);

  const [voltgraphData, setvoltGraphData] = useState([]);
  const [voltxExtent, setvoltxExtent] = useState([]);
  const [voltyExtent, setvoltyExtent] = useState([]);

  const [mvPerDay, setMvPerDay] = useState(0);
  const [daysPerBattery, setDaysPerBattery] = useState(0);

  const [annotations, setAnnotations] = useState([]);

  useEffect(() => {
    fetch(`/api/get_device/${deviceId}`)
      .then((response) => response.json())
      .then((data) => {
        setDevice(data);
      });
  }, [setDevice, deviceId]);

  useEffect(() => {
    fetch(`/api/get_sensor_data/${deviceId}/soil`)
      .then((response) => response.json())
      .then((device_data) => {
        const mappedData = processData(device_data);

        setxExtent(mappedData.xExtent);
        setyExtent(mappedData.yExtent);
        setGraphData([
          {
            key: device_data[0].device_id,
            data: mappedData.data,
          },
        ]);
      });
  }, [setxExtent, setyExtent, setGraphData, deviceId]);

  useEffect(() => {
    fetch(`/api/get_raw_sensor_data/${deviceId}/watering`)
      .then((response) => response.json())
      .then((device_data) => {
        const mappedData = processData(device_data);
        setAnnotations(mappedData.data);
      });
  }, [deviceId]);

  useEffect(() => {
    fetch(`/api/get_sensor_data/${deviceId}/volt`)
      .then((response) => response.json())
      .then((device_data) => {
        const batteryStats = calcBatteryStats(device_data);
        setMvPerDay(batteryStats.mvPerDay);
        setDaysPerBattery(batteryStats.daysPerBattery);

        const mappedData = processData(device_data);

        setvoltxExtent(mappedData.xExtent);
        setvoltyExtent(mappedData.yExtent);
        setvoltGraphData([
          {
            key: device_data[0].device_id,
            data: mappedData.data,
          },
        ]);
      });
  }, [setvoltxExtent, setvoltyExtent, setvoltGraphData, deviceId]);

  function handleWaterButtonClick() {
    fetch(`/api/do_watering/${deviceId}`);
  }

  function handleSettingsButtonClick() {
    setShowSettings(!showSettings);
  }

  function handleDismiss() {
    console.log("handle dismiss in status modal dismiss");
    setShowSettings(false);
    // setShowSettings(false);
  }

  var colorScale = scaleOrdinal(schemeCategory10);

  console.log("rerendering status modal");

  return (
    <Layer>
      <Modal
        heading={device.name}
        accessibilityModalLabel={device.name || "Status"}
        onDismiss={onDismiss}
        size="sm"
      >
        <Text align="center">
          Voltage: {device.volt}. mV per day: {Math.floor(mvPerDay)}. Days per
          battery: {Math.floor(daysPerBattery)}
        </Text>
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
              annotations={annotations}
            />
          </Box>
          <Box flex="grow" width="100%" padding={3}>
            <LineGraph
              graphData={voltgraphData}
              colorScale={colorScale}
              xExtent={voltxExtent}
              yExtent={voltyExtent}
              invert={false}
            />
          </Box>
          <Button
            onClick={handleWaterButtonClick}
            color="blue"
            paddingX={3}
            paddingY={3}
            text="Water plant!"
          />
          <Button
            onClick={handleSettingsButtonClick}
            color="blue"
            paddingX={3}
            paddingY={3}
            text="Settings"
          />

          {showSettings && (
            <SettingsModal
              deviceId={device.id}
              onDismiss={handleDismiss}
              // updateValue={updateValue}
            />
          )}
        </Box>
      </Modal>
    </Layer>
  );
}

export default StatusModal;
