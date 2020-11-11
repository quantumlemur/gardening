import React, { useEffect, useState } from "react";

import "gestalt/dist/gestalt.css";
import { Box, Button, Heading, Layer, Modal } from "gestalt";

import Map from "../HouseMap/Map";
import SettingsModal from "./SettingsModal";

function ManagementRow({ deviceId, deviceName }) {
  const [showSettings, setShowSettings] = useState(false);
  const [showMap, setShowMap] = useState(false);
  const [x, setX] = useState();
  const [y, setY] = useState();
  const [zone, setZone] = useState();
  const [canSubmit, setCanSubmit] = useState(false);

  function setLocation(event) {
    setX(
      (event.nativeEvent.offsetX /
        event.nativeEvent.target.width.baseVal.value) *
        1000
    );
    setY(
      (event.nativeEvent.offsetY /
        event.nativeEvent.target.height.baseVal.value) *
        1000
    );
    setZone(event.nativeEvent.target.id);
    setCanSubmit(true);
  }

  function submitLocation() {
    const data = {
      location_x: x,
      location_y: y,
      location_zone: zone,
    };
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    };
    fetch(`/api/submit_location/${deviceId}`, requestOptions);
  }

  return (
    <Box display="flex" paddingX={3} paddingY={3}>
      <Box display="flex" paddingX={3} paddingY={3}>
        <Heading>{deviceName}</Heading>
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
          deviceId={deviceId}
          onDismiss={() => {
            setShowSettings(!showSettings);
          }}
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
              heading={deviceName}
              accessibilityModalLabel={deviceName}
              onDismiss={() => {
                setShowMap(!showMap);
              }}
              size="lg"
            >
              <Box display="flex" direction="column">
                <Box display="flex" direction="column">
                  <Map
                    initialActiveDeviceId={deviceId}
                    setLocation={setLocation}
                  />
                </Box>
                <Box display="flex">
                  <Button
                    onClick={submitLocation}
                    paddingX={3}
                    paddingY={3}
                    text="Submit"
                    disabled={!canSubmit}
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

export default ManagementRow;
