import React, { useEffect, useState } from "react";

import "gestalt/dist/gestalt.css";
import { Box, Button, Heading, Layer, Modal } from "gestalt";

import Map from "../HouseMap/Map";
import InputField from "./InputField";
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
  const [zones, setZones] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showMap, setShowMap] = useState(false);

  useEffect(() => {
    fetch("/api/get_zones")
      .then((res) => res.json())
      .then((data) => {
        setZones(data);
      });
  }, []);

  function setLocation(event) {
    device.location_x =
      (event.nativeEvent.offsetX /
        event.nativeEvent.target.width.baseVal.value) *
      1000;
    device.location_y =
      (event.nativeEvent.offsetY /
        event.nativeEvent.target.height.baseVal.value) *
      1000;
    device.location_zone = event.nativeEvent.target.id;
    console.log(
      event.nativeEvent.offsetX,
      event.nativeEvent.target.width.baseVal.value
    );
    // console.log(event.nativeEvent.target);
    // console.log(event);
    // console.log(event.nativeEvent.target.width.baseVal.value);
  }

  function handleDismiss() {
    setShowSettings(!showSettings);
  }

  function handleSubmit(data) {
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
          currDevice={device}
          onDismiss={handleDismiss}
          // updateValue={updateValue}
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
                    zones={zones}
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
