import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";

import Map from "./HouseMap/Map"

import { Box, Heading, Text } from "gestalt";

function Status() {
  const [data, setData] = useState([]);
  const [map, setMap] = useState(0);

  useEffect(() => {
    fetch("/api/get_devices")
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        setMap(
          <Map
            devices={data}
            activeDevice={false}
          />);
      });
  }, []);

  return (
    <Box
      display="flex"
      color="gray"
      justifyContent="center"
      alignItems="center"
      width="100vw"
      height="100vh"
    >
      {map}
    </Box>
  );
}

export default Status;
