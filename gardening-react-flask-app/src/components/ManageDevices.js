import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";

import { Box, Heading, Text } from "gestalt";

function ManageDevices() {
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch("/api/time")
      .then((res) => res.json())
      .then((data) => {
        setCurrentTime(data.time);
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
      <Box padding={4}>
        <Heading size="lg" color="white">
          Manage Devices
        </Heading>
      </Box>
      <Box padding={4}>
        <Text>The current time is {currentTime}.</Text>
      </Box>
    </Box>
  );
}

export default ManageDevices;
