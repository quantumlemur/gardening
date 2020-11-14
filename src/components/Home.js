import React from "react";
import "gestalt/dist/gestalt.css";

import Map from "./HouseMap/Map";

import { Box } from "gestalt";

function Home() {
  return (
    <Box
      display="flex"
      flex="grow"
      color="lightGray"
      alignContent="center"
      // alignItems="center"
    >
      <Box
        display="flex"
        flex="grow"
        direction="column"
        alignContent="center"
        // alignItems="center"
      >
        <Map />
      </Box>
    </Box>
  );
}

export default Home;
