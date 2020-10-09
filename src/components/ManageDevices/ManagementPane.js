import React, { useState } from "react";

import "gestalt/dist/gestalt.css";
import { Box, Button, Heading, Layer, Modal } from "gestalt";

import Map from "../HouseMap/Map";
import ManagementElement from "./ManagementElement";
import SettingsModal from "./SettingsModal";

function SubmitConfig(data) {
  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  };
  fetch("/api/submit_config", requestOptions);
}

function ManagementPane({ device, alldevices }) {
  const [showSettings, setShowSettings] = useState(false);
  const [showMap, setShowMap] = useState(false);

  function updateValue(tag, value) {
    device[tag] = value;
  }

  function setLocation(event) {
    device.location_x = event.nativeEvent.offsetX;
    device.location_y = event.nativeEvent.offsetY;
  }

  function handleDismiss() {
    setShowSettings(!showSettings);
  }

  function handleSubmit(data) {
    console.log("submit", data);
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
    fetch("/api/submit_config", requestOptions);
  }

  return (
    <Box display="flex" paddingX={3} paddingY={3}>
      <Box display="flex" paddingX={3} paddingY={3}>
        <Heading>{device.name}</Heading>
      </Box>
      <Box display="flex" paddingX={3} paddingY={3}>
        <Box marginLeft={-1} marginRight={-1}>
          <Box padding={1}>
            <Button
              inline
              text="Edit settings"
              onClick={() => {
                setShowSettings(!showSettings);
              }}
            />
          </Box>
        </Box>
      </Box>
      {showSettings && (
        <SettingsModal
          device={device}
          onDismiss={handleDismiss}
          updateValue={updateValue}
          onSubmit={handleSubmit}
        />
      )}
      <Box display="flex" paddingX={3} paddingY={3}>
        <Box marginLeft={-1} marginRight={-1}>
          <Box padding={1}>
            <Button
              inline
              text="Edit map"
              onClick={() => {
                setShowMap(!showMap);
              }}
            />
          </Box>
        </Box>
        {showMap && (
          <Layer>
            <Modal
              heading={device.name}
              accessibilityModalLabel={device.name}
              onDismiss={() => {
                setShowMap(!showMap);
              }}
              size="lg"
            >
              <Box display="flex" wrap direction="column">
                <Box display="flex" direction="row" wrap>
                  <Map
                    devices={alldevices}
                    initialActiveDevice={device}
                    setLocation={setLocation}
                  />
                </Box>
                <Box display="flex">
                  <Button
                    onClick={() => SubmitConfig(device)}
                    paddingX={3}
                    paddingY={3}
                    text="Submit"
                  />
                </Box>
              </Box>
            </Modal>
          </Layer>
        )}
      </Box>
    </Box>
  );
}

export default ManagementPane;
