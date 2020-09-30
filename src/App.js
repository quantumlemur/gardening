import React from "react";
import ManageDevices from "./components/ManageDevices";
import Graph from "./components/Graph";
import Home from "./components/Home";
import Navigation from "./components/Navigation";
import Error from "./components/Error";

import { BrowserRouter, Route, Switch, useParams } from "react-router-dom";

import { Box } from "gestalt";

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Switch>
        <Route path="/" component={Home} exact />
        <Route path="/manage/:id">
          <ManageDevices />
        </Route>
        <Route path="/graph/">
          <Graph />
        </Route>
        <Route path="/test/:id">
          <TestId />
        </Route>
        <Route component={Error} />
      </Switch>
    </BrowserRouter>
  );
}

function TestId() {
  let params = useParams();
  return <Box padding={4}>URL params: {params.id}</Box>;
}

export default App;
