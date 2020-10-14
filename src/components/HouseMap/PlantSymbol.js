import React, { useState } from "react";
import { Icon } from "gestalt";
import { animated } from "react-spring";
import { Keyframes } from "react-spring/renderprops";

function Circle({ color, pulse }) {
  const Chain = Keyframes.Spring(async (next) => {
    while (true) {
      await next({
        from: { r: 5 },
        to: { r: 20 },
      });
      await next({
        from: { r: 20 },
        to: { r: 5 },
      });
    }
  });

  if (pulse) {
    return (
      <Chain>{(props) => <animated.circle style={props} fill={color} />}</Chain>
    );
  } else {
    return <circle r="8" fill={color} />;
  }
}

function Alert() {
  return (
    <g transform="translate(-16, 0)">
      <Icon icon="alert" accessibilityLabel="alert" color="darkGray" />
    </g>
  );
}

function LightningBolt() {
  return (
    <Icon
      icon="lightning-bolt-circle"
      accessibilityLabel="lightning-bolt-circle"
      color="darkGray"
      inline="true"
    />
  );
}

function PlantSymbol({
  data,
  index,
  onClick,
  color,
  pulse,
  needCharge,
  alert,
}) {
  return (
    <g
      transform={`translate(${data.location_x}, ${data.location_y})`}
      draggable
      onClick={() => onClick(data)}
    >
      <Circle color={color} pulse={pulse} />
      {alert && <Alert />}
      {needCharge && <LightningBolt />}
    </g>
  );
}

export default PlantSymbol;
