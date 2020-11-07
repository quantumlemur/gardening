import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";

import Map from "./HouseMap/Map";

import { Box, Heading, Text } from "gestalt";

function Home() {
  const [devices, setDevices] = useState([]);
  const [zones, setZones] = useState([]);

  useEffect(() => {
    fetch("/api/get_devices")
      .then((res) => res.json())
      .then((data) => {
        setDevices(data);
      });
  }, []);

  useEffect(() => {
    fetch("/api/get_zones")
      .then((res) => res.json())
      .then((data) => {
        setZones(data);
      });
  }, []);

  return (
    <Box
      display="flex"
      flex="grow"
      color="lightGray"
      justifyContent="center"
      alignItems="center"
    >
      <Box display="flex" direction="column" alignContent="center">
        <Map devices={devices} zones={zones} />
      </Box>
    </Box>
  );
}

export default Home;
