import React from "react";
import "gestalt/dist/gestalt.css";
import ManageDevices from "./components/ManageDevices";
import Home from "./components/Home";
import Navigation from "./components/Navigation";

import { BrowserRouter, Route, Switch } from "react-router-dom";

import { Box } from "gestalt";

function App() {
  return (
    <BrowserRouter>
      <Box>
        <Navigation />
        <Switch>
          <Route path="/" component={Home} exact />
          <Route path="/manage" component={ManageDevices} />
          <Route component={Error} />
        </Switch>
      </Box>
    </BrowserRouter>
  );
}

export default App;
