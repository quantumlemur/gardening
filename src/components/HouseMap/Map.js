import React, { useEffect, useRef, useState } from "react";
import "gestalt/dist/gestalt.css";
import { Box, Heading, Image } from "gestalt";
import { scaleLinear } from "d3-scale";

import PlantShadow from "./PlantShadow";
import PlantSymbol from "./PlantSymbol";
import StatusModal from "../ManageDevices/StatusModal";

function Map({ initialActiveDeviceId, setLocation }) {
  const [activeDeviceId, setActiveDeviceId] = useState(initialActiveDeviceId);
  const [devices, setDevices] = useState([]);
  const [zones, setZones] = useState([]);
  const [showStatus, setShowStatus] = useState(false);
  const [width, setWidth] = useState(0);

  const ref = useRef(null);

  useEffect(() => {
    fetch("/api/get_zones")
      .then((res) => res.json())
      .then((data) => {
        setZones(data);
      });
  }, []);

  useEffect(() => {
    fetch("/api/get_devices")
      .then((res) => res.json())
      .then((data) => {
        setDevices(data);
      });
  }, []);

  useEffect(() => {
    setWidth(ref.current.clientWidth);
  }, [ref]);

  const handlePlantClick = (device) => {
    setActiveDeviceId(device.id);
    setShowStatus(!showStatus);
    // setShowSettings(!showSettings);
  };

  function handleDismiss() {
    setShowStatus(false);
    // setShowSettings(false);
  }

  // const activeDeviceId = activeDevice.id || "No device active";
  // const activeHeader = "Active device: ";

  var colorScale = scaleLinear().domain([0, 1]).range(["green", "brown"]);

  const xScale = scaleLinear().domain([0, 1000]).range([0, width]);

  const zoneBoxes = zones.map((z, i) => {
    const scalingFactor = width / z.image_width;
    const scaledHeight = scalingFactor * z.image_height;
    const yScale = scaleLinear().domain([0, 1000]).range([0, scaledHeight]);
    return (
      <Box key={z.zone_id}>
        <Image
          key={z.zone_id}
          src={z.file_name}
          alt={z.zone_name}
          naturalWidth={z.image_width}
          naturalHeight={z.image_height}
        >
          <Box flex-grow="1" height="100%" width="100%" position="absolute">
            <svg
              width="100%"
              height="100%"
              onClick={setLocation}
              key={z.zone_id}
              id={z.zone_id}
              // viewBox="0 0 1000 1000"
              // preserveAspectRatio="none"
            >
              <defs>
                <radialGradient id="shadow">
                  <stop offset="25%" stopColor="white" stopOpacity="1" />
                  <stop offset="75%" stopColor="white" stopOpacity="0" />
                </radialGradient>
              </defs>
              {devices
                .filter((device) => device.location_zone === z.zone_id)
                .map((d, i) => (
                  <PlantShadow
                    key={d.id}
                    x={xScale(d.location_x)}
                    y={yScale(d.location_y)}
                  />
                ))}
              {devices
                .filter((device) => device.location_zone === z.zone_id)
                .map((d, i) => (
                  <PlantSymbol
                    key={d.id}
                    data={d}
                    index={i}
                    x={xScale(d.location_x)}
                    y={yScale(d.location_y)}
                    onClick={handlePlantClick}
                    pulse={d.id === activeDeviceId}
                    color={colorScale(d.calibrated_value)}
                    needWater={d.calibrated_value > 0.8}
                    needCharge={d.board_type !== 1 && d.volt < 3600}
                    alert={new Date() > d.device_next_init * 1000}
                  />
                ))}
            </svg>
          </Box>
        </Image>
      </Box>
    );
  });

  return (
    <Box
      display="flex"
      flex="grow"
      direction="column"
      alignContent="center"
      // alignItems="center"
      maxWidth={800}
      ref={ref}
    >
      {/* <Box>
        <Heading>
          {activeHeader}
          {activeDeviceId}
        </Heading>
      </Box> */}
      {zoneBoxes}

      {showStatus && (
        <StatusModal
          deviceId={activeDeviceId}
          // onSettingsButtonClick={handleSettingsButtonClick}
          onDismiss={handleDismiss}
        />
      )}
    </Box>
  );
}

export default Map;
