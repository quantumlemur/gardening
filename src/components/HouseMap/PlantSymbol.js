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
    return <circle r="10" fill={color} />;
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
    />
  );
}

function Dropper() {
  return (
    <g transform="translate(-5, -27)">
      <Icon
        icon="color-picker"
        accessibilityLabel="color-picker"
        color="black"
        size="28"
      />
    </g>
  );
}

function PlantSymbol({
  data,
  index,
  x,
  y,
  onClick,
  color,
  pulse,
  needWater,
  needCharge,
  alert,
}) {
  return (
    <g
      transform={`translate(${x}, ${y})`}
      draggable
      onClick={() => onClick(data)}
    >
      <Circle color={color} pulse={pulse} />
      {needWater && <Dropper />}
      {alert && <Alert />}
      {needCharge && <LightningBolt />}
    </g>
  );
}

export default PlantSymbol;
