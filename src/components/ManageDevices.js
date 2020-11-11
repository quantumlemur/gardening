import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";

import ManagementRow from "./ManageDevices/ManagementRow";

import { Box } from "gestalt";

function ManageDevices() {
  const [deviceList, setDeviceList] = useState([]);

  useEffect(() => {
    fetch("/api/get_device_list")
      .then((res) => res.json())
      .then((data) => {
        setDeviceList(data);
      });
  }, []);

  return (
    <Box display="flex" direction="column" width="100%">
      {deviceList.map((device, index) => (
        <ManagementRow
          key={device.id}
          deviceId={device.id}
          deviceName={device.name}
        />
      ))}
    </Box>
  );
}

export default ManageDevices;
