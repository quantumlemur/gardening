import React, { useState } from "react";

import "gestalt/dist/gestalt.css";
import { Box, Button, Heading, Layer, Modal } from "gestalt";

import Map from "../HouseMap/Map"
import ManagementElement from "./ManagementElement";



function SubmitConfig(data) {
	
	const requestOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
	};
	fetch("/api/submit_config", requestOptions)

}


function ManagementPane({device, alldevices}) {

	const [showSettings, setShowSettings] = useState(false);
	const [showMap, setShowMap] = useState(false);


	function updateValue(tag, value) {
		device[tag] = value;
	}
	

	function SetLocation(event) {
		device.location_x = event.nativeEvent.offsetX;
		device.location_y = event.nativeEvent.offsetY;
	}


	return (
		<Box display="flex" paddingX={3} paddingY={3}>
			<Box display="flex" paddingX={3} paddingY={3}>
				<Heading>
					{device.name}
				</Heading>
			</Box>
			<Box display="flex" paddingX={3} paddingY={3}>
				<Box marginLeft={-1} marginRight={-1}>
					<Box padding={1}>
						<Button
							inline
							text="Edit settings"
							onClick={() => { setShowSettings(!showSettings)}}
						/>
					</Box>
				</Box>
				{showSettings && (
					<Layer>
						<Modal
							heading={device.name}
							accessibilityModalLabel={device.name}
							onDismiss={() => { setShowSettings(!showSettings)}}
							size="lg"
							>
							<Box
								display="flex"
								wrap
								width="100%"
								direction="column"
							>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<Box
										display="flex"
										wrap
									>
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
									<Box
										display="flex"
										wrap
									>
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
									<Box
										display="flex"
										wrap
									>
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
									<Box
										display="flex"
										wrap
									>
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
									onClick={() => SubmitConfig(device)}
									paddingX={3}
									paddingY={3}
									text="Submit" />
							</Box>
						</Modal>
					</Layer>
				)}
			</Box>
			<Box display="flex" paddingX={3} paddingY={3}>
				<Box marginLeft={-1} marginRight={-1}>
					<Box padding={1}>
						<Button
							inline
							text="Edit map"
							onClick={() => { setShowMap(!showMap)}}
						/>
					</Box>
				</Box>
				{showMap && (
					<Layer>
						<Modal
							heading={device.name}
							accessibilityModalLabel={device.name}
							onDismiss={() => { setShowMap(!showMap)}}
							size="lg" >
							<Box
								display="flex"
								wrap
								direction="column"
								onClick={SetLocation} >
								<Box
									display="flex"
									direction="row"
									wrap>
									<Map
										devices={alldevices}
										activeDevice={device} />
								</Box>
								<Box
									display="flex">
									<Button
										onClick={() => SubmitConfig(device)}
										paddingX={3}
										paddingY={3}
										text="Submit" />
								</Box>
							</Box>
						</Modal>
					</Layer>
				)}
			</Box>
		</Box>
	);

}

export default ManagementPane;