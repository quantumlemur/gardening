import React from "react";
import { Box, Heading, Image } from "gestalt";

const Error = () => {
  return (
    <Box
      display="flex"
      direction="column"
      justifyContent="center"
      alignItems="center"
    >
      <Box padding={4}>
        <Heading size="md">Sowwy - this page no existe</Heading>
        <Box marginTop={3}>
          <Box width="400px" height="400px">
            <Image
              src="https://i.imgur.com/h7p7cuR.jpg"
              // src="https://i.ibb.co/7bQQYkX/stock2.jpg"
              naturalHeight={4032}
              naturalWidth={3024}
            />
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Error;
