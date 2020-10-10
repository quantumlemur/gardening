import React, { useState, useEffect } from "react";

import { Box, Button, Modal, Layer, Switch, Text } from "gestalt";
import InputField from "./InputField";

function SettingsModal({ currDevice, onDismiss, updateValue, onSubmit }) {
  const [device, setDevice] = useState(currDevice);
  const [name, setName] = useState(currDevice.name);
  const [initInterval, setInitInterval] = useState(currDevice.INIT_INTERVAL);
  const [sleepDuration, setSleepDuration] = useState(currDevice.SLEEP_DURATION);
  const [maxEntries, setMaxEntries] = useState(
    currDevice.MAX_ENTRYS_WITHOUT_INIT
  );
  const [light, setLight] = useState(currDevice.LIGHT);

  function handleLight(value) {
    if (value) {
      setLight(1);
    } else {
      setLight(0);
    }
  }

  return (
    <Layer>
      <Modal
        heading={device.name}
        accessibilityModalLabel={device.name}
        onDismiss={onDismiss}
        size="lg"
      >
        <Box
          display="flex"
          wrap
          width="100%"
          direction="column"
          paddingX={3}
          paddingY={3}
        >
          <Box display="flex">
            <Box column={6}>
              <InputField
                varName="NAME"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Box>
            <Box column={6}>
              <InputField varName="mac" value={device.mac} disabled />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                varName="checkin_time"
                label="LAST SEEN"
                value={device.checkin_time}
                disabled
              />
            </Box>
            <Box column={6}>
              <InputField
                varName="device_next_init"
                label="Next expected"
                value={device.device_next_init}
                disabled
              />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                varName="INIT_INTERVAL"
                value={initInterval}
                onChange={(e) => setInitInterval(e.target.value)}
                placeholder="Max time between INIT boots (wifi)"
                type="number"
                allowedType="positiveInt"
              />
            </Box>
            <Box column={6}>
              <InputField
                varName="SLEEP_DURATION"
                value={sleepDuration}
                placeholder="Sleep time (sec)"
                onChange={(e) => setSleepDuration(e.target.value)}
                type="number"
                allowedType="positiveInt"
              />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                varName="MAX_ENTRYS_WITHOUT_INIT"
                value={maxEntries}
                onChange={(e) => setMaxEntries(e.target.value)}
                placeholder="Max boots before going to INIT"
                type="number"
                allowedType="positiveInt"
              />
            </Box>
            <Box column={6}>
              <Box display="flex" direction="column" padding={3}>
                <Box>
                  <Text>{"Light"}</Text>
                </Box>
                <Box paddingY={1}>
                  <Switch
                    name="Light"
                    switched={light === 1}
                    onChange={(e) => handleLight(e.value)}
                    placeholder="Light? 1/0"
                  />
                </Box>
              </Box>
            </Box>
          </Box>

          <Button
            onClick={() => onSubmit(device)}
            paddingX={3}
            paddingY={3}
            text="Submit"
          />
        </Box>
      </Modal>
    </Layer>
  );
}

export default SettingsModal;
