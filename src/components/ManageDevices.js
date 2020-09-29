import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useParams } from "react-router-dom";

import { Box, Heading, Text } from "gestalt";

function ManageDevices() {
  const [currentTime, setCurrentTime] = useState(0);

  const params = useParams();

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
      <Box padding={4} direction="column">
        <Heading size="lg" color="white">
          Manage Device: {params.id}
        </Heading>
        <Box padding={4}>
          <Text>The current time is {currentTime}.</Text>
        </Box>
      </Box>
    </Box>
  );
}

export default ManageDevices;
