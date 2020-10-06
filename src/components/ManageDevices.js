import React, { useState, useEffect } from "react";
import "gestalt/dist/gestalt.css";
import { useParams } from "react-router-dom";

import ManagementPane from "./ManageDevices/ManagementPane"

import { Box, Heading, Text } from "gestalt";

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
			color="gray"
			justifyContent="center"
			alignItems="center"
			width="100vw"
			height="100vh"
		>
			{deviceList.map((device, index) => (
				<ManagementPane key={index} device={device} alldevices={deviceList}/>
			))}
		</Box>
	);
}

export default ManageDevices;
