import React from "react";
import { Box, Text, Heading, Link } from "gestalt";

// import { NavLink } from "react-router-dom";
// <NavLink to={props.path}>
function NavItem(props) {
  return (
    <Link href={props.path}>
      <Box paddingX={2}>
        <Heading color="white" size="sm">
          {props.label}
        </Heading>
      </Box>
    </Link>
  );
}

const Navigation = () => {
  return (
    <Box display="flex" direction="row" height="60px" color="pine">
      <Box display="flex" direction="row" alignItems="center">
        <NavItem path="/" label="Home" />
        <NavItem path="/status" label="Status" />
        <NavItem path="/graph" label="Graph" />
        <NavItem path="/manage" label="Manage" />
        <NavItem path="/test/123" label="Test URL Params" />
      </Box>
    </Box>
  );
};

export default Navigation;
