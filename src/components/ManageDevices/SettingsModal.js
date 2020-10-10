import React from "react";

import { Box, Button, Modal, Layer } from "gestalt";
import ManagementElement from "./ManagementElement";

function SettingsModal({ device, onDismiss, updateValue, onSubmit }) {
  return (
    <Layer>
      <Modal
        heading={device.name}
        accessibilityModalLabel={device.name}
        onDismiss={onDismiss}
        size="lg"
      >
        <Box display="flex" wrap width="100%" direction="column">
          <Box flex="grow" paddingX={3} paddingY={3}>
            <Box display="flex" wrap>
              <ManagementElement
                varName="name"
                value={device.name}
                updateValue={updateValue}
              />
              <ManagementElement
                varName="mac"
                value={device.mac}
                updateValue={updateValue}
                disabled
              />
            </Box>
          </Box>

          <Box flex="grow" paddingX={3} paddingY={3}>
            <Box display="flex" wrap>
              <ManagementElement
                varName="checkin_time"
                label="Last seen"
                value={device.checkin_time}
                updateValue={updateValue}
                disabled
                date
              />
              <ManagementElement
                varName="device_next_init"
                label="Next expected"
                value={device.device_next_init}
                updateValue={updateValue}
                disabled
                date
              />
            </Box>
          </Box>

          <Box flex="grow" paddingX={3} paddingY={3}>
            <Box display="flex" wrap>
              <ManagementElement
                varName="INIT_INTERVAL"
                value={device.INIT_INTERVAL}
                updateValue={updateValue}
                placeholder="Max time between INIT boots (wifi)"
                allowedType="positiveInt"
              />
              <ManagementElement
                varName="SLEEP_DURATION"
                value={device.SLEEP_DURATION}
                updateValue={updateValue}
                placeholder="Sleep time (sec)"
                allowedType="positiveInt"
              />
            </Box>
          </Box>

          <Box flex="grow" paddingX={3} paddingY={3}>
            <Box display="flex" wrap>
              <ManagementElement
                varName="MAX_ENTRYS_WITHOUT_INIT"
                value={device.MAX_ENTRYS_WITHOUT_INIT}
                updateValue={updateValue}
                placeholder="Max boots before going to INIT"
                allowedType="positiveInt"
              />
              <ManagementElement
                varName="LIGHT"
                value={device.LIGHT}
                updateValue={updateValue}
                placeholder="Light? 1/0"
                allowedType="bool"
              />
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
