import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";

import { Box, Heading, Text } from "gestalt";

function Home() {
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
      color="lightGray"
      justifyContent="center"
      alignItems="center"
      width="100vw"
      height="100vh"
    >
      <Heading size="lg" color="white">
        Learn React meow
      </Heading>
      <Box display="flex" color="blue" direction="column" alignContent="center">
        <Box padding={4}></Box>
        <Box padding={4}>
          <Text>The current time is {currentTime}.</Text>
        </Box>
      </Box>
    </Box>
  );
}

export default Home;
