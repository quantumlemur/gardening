import React, { useState } from "react";

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
  const [errorMessages, setErrorMessages] = useState({
    nameError: "",
    initIntervalError: "",
    sleepDurationError: "",
    maxEntriesError: "",
    lightError: "",
  });
  const [canSubmit, setCanSubmit] = useState(true);

  // function checkIsValid() {
  //   if (
  //     errorMessages.nameError ||
  //     errorMessages.initIntervalError ||
  //     errorMessages.sleepDurationError ||
  //     errorMessages.maxEntriesError ||
  //     errorMessages.lightError
  //   ) {
  //     return false;
  //   }
  //   return true;
  // }

  function checkFieldExists(value, errorName) {
    let message = "";
    if (!value) {
      message = "Field must not be blank";
      setCanSubmit(false);
    } else {
      setCanSubmit(true);
    }
    setErrorMessages({ [errorName]: message });
  }

  function checkPositiveValue(value, errorName) {
    let message = "";
    if (value <= 0) {
      message = "Must be a positive integer";
      setCanSubmit(false);
    } else {
      setCanSubmit(true);
    }
    setErrorMessages({ [errorName]: message });
  }

  function handleNameChange(value) {
    checkFieldExists(value, "nameError");
    setName(value);
  }

  function handleInitIntervalChange(value) {
    checkPositiveValue(value, "initIntervalError");
    setInitInterval(value);
  }

  function handleMaxEntriesChange(value) {
    checkPositiveValue(value, "maxEntriesError");
    setMaxEntries(value);
  }

  function handleSleepDurationChange(value) {
    checkPositiveValue(value, "sleepDurationError");
    setSleepDuration(value);
  }

  function handleLight(value) {
    if (value) {
      setLight(1);
    } else {
      setLight(0);
    }
  }

  function handleSubmit() {
    // const isValid = checkIsValid();
    // if (isValid) {
    device.name = name;
    device.INIT_INTERVAL = initInterval;
    device.SLEEP_DURATION = sleepDuration;
    device.MAX_ENTRYS_WITHOUT_INIT = maxEntries;
    device.LIGHT = light;
    setDevice(device);
    onSubmit(device);
    onDismiss();
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
                name="NAME"
                value={name}
                onChange={(e) => handleNameChange(e.target.value)}
                errorMessage={errorMessages.nameError}
              />
            </Box>
            <Box column={6}>
              <InputField name="mac" value={device.mac} disabled />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                name="checkin_time"
                label="LAST SEEN"
                value={device.checkin_time}
                type="timestamp"
                disabled
              />
            </Box>
            <Box column={6}>
              <InputField
                name="device_next_init"
                label="Next expected"
                value={device.device_next_init}
                type="timestamp"
                disabled
              />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                name="INIT_INTERVAL"
                value={initInterval}
                onChange={(e) => handleInitIntervalChange(e.target.value)}
                placeholder="Max time between INIT boots (wifi)"
                type="number"
                errorMessage={errorMessages.initIntervalError}
              />
            </Box>
            <Box column={6}>
              <InputField
                name="SLEEP_DURATION"
                value={sleepDuration}
                placeholder="Sleep time (sec)"
                onChange={(e) => handleSleepDurationChange(e.target.value)}
                type="number"
                errorMessage={errorMessages.sleepDurationError}
              />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                name="MAX_ENTRYS_WITHOUT_INIT"
                value={maxEntries}
                onChange={(e) => handleMaxEntriesChange(e.target.value)}
                placeholder="Max boots before going to INIT"
                type="number"
                errorMessage={errorMessages.maxEntriesError}
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
            onClick={handleSubmit}
            color="blue"
            paddingX={3}
            paddingY={3}
            text="Submit"
            disabled={!canSubmit}
          />
        </Box>
      </Modal>
    </Layer>
  );
}

export default SettingsModal;
