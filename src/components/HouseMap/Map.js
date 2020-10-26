import React, { useState } from "react";
import "gestalt/dist/gestalt.css";
import { Box, Heading } from "gestalt";
import { scaleLinear } from "d3-scale";

import PlantSymbol from "./PlantSymbol";
import SettingsModal from "../ManageDevices/SettingsModal";

function Map({ devices, initialActiveDevice, setLocation }) {
  const [data, setData] = useState(devices);
  const [activeDevice, setActiveDevice] = useState(
    initialActiveDevice ? initialActiveDevice : {}
  );
  const [showSettings, setShowSettings] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  function handleSubmit(data) {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
    fetch("/api/submit_config", requestOptions);
  }

  const width = 640,
    height = 400;

  const handleClick = (device) => {
    setActiveDevice(device);
    setShowSettings(!showSettings);
  };

  function handleDismiss() {
    setShowSettings(!showSettings);
  }

  const activeDeviceId = activeDevice.id || "No device active";
  const activeHeader = "Active device: ";

  var colorScale = scaleLinear().domain([0, 1]).range(["green", "brown"]);

  const plants = data.map((d, i) => (
    <PlantSymbol
      key={d.id}
      data={d}
      index={i}
      onClick={handleClick}
      pulse={d.id === activeDeviceId}
      color={colorScale(d.calibrated_value)}
      needCharge={d.volt < 3000}
      alert={new Date() > d.device_next_init * 1000}
    />
  ));

  return (
    <Box display="flex" direction="column">
      <Box>
        <Heading>
          {activeHeader}
          {activeDeviceId}
        </Heading>
      </Box>
      <svg width={width} height={height} onClick={setLocation}>
        <image href="/zone0.png" x="0" y="0" width={width} height={height} />
        <g>{plants}</g>
      </svg>
      {showSettings && (
        <SettingsModal
          currDevice={activeDevice}
          onDismiss={handleDismiss}
          // updateValue={updateValue}
          onSubmit={handleSubmit}
        />
      )}
    </Box>
  );
}

export default Map;
