import React, { useEffect, useState } from "react";

import { Box, Button, Modal, Layer, SelectList, Switch, Text } from "gestalt";
import InputField from "./InputField";

function SettingsModal({ currDevice, onDismiss, updateValue, onSubmit }) {
  const [device, setDevice] = useState(currDevice);
  const [name, setName] = useState(currDevice.name);
  const [requestedVersion, setRequestedVersion] = useState(
    currDevice.requested_version_tag
  );
  const [boardType, setBoardType] = useState(currDevice.board_type);
  const [initInterval, setInitInterval] = useState(currDevice.INIT_INTERVAL);
  const [sleepDuration, setSleepDuration] = useState(currDevice.SLEEP_DURATION);
  const [maxEntries, setMaxEntries] = useState(
    currDevice.MAX_ENTRYS_WITHOUT_INIT
  );
  const [light, setLight] = useState(currDevice.LIGHT);
  const [errorMessages, setErrorMessages] = useState({
    nameError: "",
    requestedVersionError: "",
    boardTypeError: "",
    initIntervalError: "",
    sleepDurationError: "",
    maxEntriesError: "",
    lightError: "",
  });
  const [canSubmit, setCanSubmit] = useState(true);
  const [firmwareVersionsAvailable, setFirmwareVersionsAvailable] = useState(
    []
  );
  const [boardTypesAvailable, setBoardTypesAvailable] = useState([]);

  useEffect(() => {
    fetch("/api/get_firmware_versions")
      .then((response) => response.json())
      .then((data) => {
        data.unshift({ label: "None (always stay updated)", value: "" });
        setFirmwareVersionsAvailable(data);
      });
  }, []);

  useEffect(() => {
    fetch("/api/get_board_types")
      .then((response) => response.json())
      .then((data) => {
        setBoardTypesAvailable(data);
      });
  }, []);

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

  // function checkVersionExists(value, errorName) {
  //   let message = "";
  //   if (~versionsAvailable.includes(value)) {
  //     message = "Version not available";
  //     setCanSubmit(false);
  //   } else {
  //     setCanSubmit(true);
  //   }
  //   setErrorMessages({ [errorName]: message });
  // }

  function handleNameChange(value) {
    checkFieldExists(value, "nameError");
    setName(value);
  }

  function handleRequestedVersionChange(value) {
    // checkVersionExists(value, "requestedVersionError");
    // console.log(value);
    setRequestedVersion(value);
  }

  function handleBoardTypeChange(value) {
    setBoardType(value);
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
    device.requested_version_tag = requestedVersion;
    device.board_type = boardType;
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
                type="datetime-local"
                disabled
              />
            </Box>
            <Box column={6}>
              <InputField
                name="device_next_init"
                label="Next expected"
                value={device.device_next_init}
                type="datetime-local"
                disabled
              />
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <InputField
                name="firmware_version"
                label="Frmware version"
                value={device.current_version_tag}
                disabled
              />
            </Box>
            <Box column={6}>
              <Box flex="grow" padding={3}>
                <SelectList
                  id="requested_version"
                  name="requested_version"
                  label="Requested firmware version"
                  value={requestedVersion}
                  options={firmwareVersionsAvailable}
                  onChange={({ value }) => handleRequestedVersionChange(value)}
                />
              </Box>
            </Box>
          </Box>

          <Box display="flex">
            <Box column={6}>
              <Box flex="grow" padding={3}>
                <SelectList
                  id="board_type"
                  name="board_type"
                  label="Board type"
                  value={boardType}
                  options={boardTypesAvailable}
                  onChange={({ value }) => handleBoardTypeChange(value)}
                />
              </Box>
            </Box>
            <Box column={6}></Box>
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
                    id="Light"
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
