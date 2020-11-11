import React, { useEffect, useState } from "react";

import { Box, Button, Modal, Layer, SelectList, Switch, Text } from "gestalt";
import InputField from "./InputField";

function SettingsModal({ deviceId, onDismiss }) {
  const [device, setDevice] = useState({});
  const [requestedVersionTag, setRequestedVersionTag] = useState("");
  const [boardType, setboardType] = useState("");
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
    fetch(`/api/get_device/${deviceId}`)
      .then((response) => response.json())
      .then((data) => {
        setDevice(data);
        setRequestedVersionTag(data.requested_version_tag);
        setboardType(String(data.board_type));
      });
  }, []);

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
        const stringifiedData = data.map((d) => ({
          label: d.label,
          value: String(d.value),
        }));
        setBoardTypesAvailable(stringifiedData);
      });
  }, []);

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
    setDevice((device) => Object.assign(device, { name: value }));
  }

  function handleRequestedVersionChange(value) {
    setDevice((device) =>
      Object.assign(device, { requested_version_tag: value })
    );
    setRequestedVersionTag(value);
  }

  function handleBoardTypeChange(value) {
    setDevice((device) =>
      Object.assign(device, { board_type: parseInt(value) })
    );
    setboardType(String(value));
  }

  function handleInitIntervalChange(value) {
    checkPositiveValue(value, "initIntervalError");
    setDevice((device) => Object.assign(device, { INIT_INTERVAL: value }));
  }

  function handleMaxEntriesChange(value) {
    checkPositiveValue(value, "maxEntriesError");
    setDevice((device) =>
      Object.assign(device, { MAX_ENTRYS_WITHOUT_INIT: value })
    );
  }

  function handleSleepDurationChange(value) {
    checkPositiveValue(value, "sleepDurationError");
    setDevice((device) => Object.assign(device, { SLEEP_DURATION: value }));
  }

  function handleLight(value) {
    setDevice((device) => Object.assign(device, { LIGHT: value ? 1 : 0 }));
  }

  function handleSubmit() {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(device),
    };
    fetch("/api/submit_config", requestOptions);
    onDismiss();
  }

  return (
    <Layer>
      <Modal
        heading={device.name}
        accessibilityModalLabel={device.name || "Settings"}
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
                value={device.name}
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
                  value={requestedVersionTag}
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
                value={device.INIT_INTERVAL}
                onChange={(e) => handleInitIntervalChange(e.target.value)}
                placeholder="Max time between INIT boots (wifi)"
                type="number"
                errorMessage={errorMessages.initIntervalError}
              />
            </Box>
            <Box column={6}>
              <InputField
                name="SLEEP_DURATION"
                value={device.SLEEP_DURATION}
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
                value={device.MAX_ENTRYS_WITHOUT_INIT}
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
                    switched={device.LIGHT === 1}
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
