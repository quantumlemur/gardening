import React, { useState } from "react";
import "gestalt/dist/gestalt.css";
import { Box, Heading } from "gestalt";
import { useSpring, animated } from "react-spring";
import { scaleLinear } from "d3-scale";
import PlantSymbol from "./PlantSymbol";

function Map({ devices }) {
  const [data, setData] = useState(devices);
  const [activeDevice, setActiveDevice] = useState({});
  const [isModalOpen, setIsModalOpen] = useState(false);

  const props = useSpring({
    from: { r: 0 },
    to: { r: 10 },
  });

  var colorScale = scaleLinear().domain([0, 1]).range(["green", "brown"]);

  const width = 640,
    height = 400;

  const handleClick = (device) => {
    setActiveDevice(device);
    setIsModalOpen(!!isModalOpen);
  };
  const plants = data.map((d, i) => (
    <PlantSymbol data={d} index={i} onClick={handleClick} />
  ));

  const activeDeviceId = activeDevice.id || "No device active";
  const activeHeader = "Active device: ";

  return (
    <Box display="flex" direction="column">
      <Box>
        <Heading>
          {activeHeader}
          {activeDeviceId}
        </Heading>
      </Box>
      <svg width={width} height={height}>
        <image href="/zone0.png" x="0" y="0" width={width} height={height} />
        <g>{plants}</g>
      </svg>
    </Box>
  );
}

export default Map;
