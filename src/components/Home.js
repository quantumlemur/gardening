import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";

import Map from "./HouseMap/Map";

import { Box, Heading, Text } from "gestalt";

function Home() {
  const [devices, setDevices] = useState([]);
  const [map, setMap] = useState(0);

  useEffect(() => {
    fetch("/api/get_devices")
      .then((res) => res.json())
      .then((data) => {
        setDevices(data);
        setMap(<Map devices={data} activeDevice={false} />);
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
        {map}
      </Box>
    </Box>
  );
}

export default Home;
