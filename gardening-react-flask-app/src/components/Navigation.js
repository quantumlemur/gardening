import React from "react";
import { Box, Text } from "gestalt";

import { NavLink } from "react-router-dom";

function NavItem(props) {
  return (
    <Box paddingX={2}>
      <NavLink to={props.path}>
        <Text color="white" size="lg">
          {props.label}
        </Text>
      </NavLink>
    </Box>
  );
}

const Navigation = () => {
  return (
    <Box
      display="flex"
      direction="row"
      width="100vw"
      color="pine"
      justifyContent="start"
    >
      <NavItem path="/" label="Home" />
      <NavItem path="/manage" label="Manage" />
    </Box>
  );
};

export default Navigation;
