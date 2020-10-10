import React from "react";
import ManageDevices from "./components/ManageDevices";
import Graph from "./components/Graph";
import RawGraph from "./components/RawGraph";
import Home from "./components/Home";
import Navigation from "./components/Navigation";
import Error from "./components/Error";

import { BrowserRouter, Route, Switch, useParams } from "react-router-dom";

import { Box } from "gestalt";

function App() {
  return (
    <BrowserRouter>
      <Box display="flex" direction="column" minHeight="100vh">
        <Navigation />
        <Box
          display="flex"
          color="gray"
          // justifyContent="center"
          // alignItems="center"
          flex="grow"
        >
          <Switch>
            <Route path="/" component={Home} exact />
            <Route path="/manage/">
              <ManageDevices />
            </Route>
            <Route path="/graph/">
              <Graph />
            </Route>
            <Route path="/rawgraph/">
              <RawGraph />
            </Route>
            <Route path="/test/:id">
              <TestId />
            </Route>
            <Route component={Error} />
          </Switch>
        </Box>
        <Box color="blue">{"footer"}</Box>
      </Box>
    </BrowserRouter>
  );
}

function TestId() {
  let params = useParams();
  return <Box padding={4}>URL params: {params.id}</Box>;
}

export default App;
