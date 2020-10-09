import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useParams } from "react-router-dom";

import ManagementPane from "./ManageDevices/ManagementPane"

import { Box } from "gestalt";

function ManageDevices() {
	const [deviceList, setDeviceList] = useState([]);

	const params = useParams();

	useEffect(() => {
		fetch("/api/get_devices")
			.then((res) => res.json())
			.then((data) => {
				setDeviceList(data);
			});
	}, []);


	return (
		<Box
			display="flex"
			direction="column"
			width="100%"
		>
			{deviceList.map((device, index) => (
				<ManagementPane key={index} device={device} alldevices={deviceList}/>
			))}
		</Box>
	);
}

export default ManageDevices;
