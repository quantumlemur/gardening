import React, { useState } from "react";
import "gestalt/dist/gestalt.css";

import 'bootstrap/dist/css/bootstrap.css';
import { Button, Card, Col, Collapse, Form, Row } from 'react-bootstrap';

import Map from "../HouseMap/Map"

import { Box, Heading, TextField } from "gestalt";



function SubmitConfig(data) {
	
	const requestOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
	};
	fetch("/api/submit_config", requestOptions)

}


function ManagementPane({device, alldevices}) {

	const [open, setOpen] = useState(false);
	const [formData, setFormData] = useState(device)

	function handleInputChange(event) {
		const target = event.event.target;
		// console.log(event)
		// console.log(event.event)
		// console.log(event.event.target)
    const value = target.value;
		const name = target.name;

		// this is DEFINITELY not the right way to do this.  omg.
		// var newFormData = formData;
		// console.log(name, value)
		formData[name] = value;

		// setFormData(newFormData);

	}
	

	function SetLocation(event) {
		const newFormData = formData;
		formData.location_x = event.nativeEvent.offsetX;
		formData.location_y = event.nativeEvent.offsetY;
	}


	return (
		<Card>
			<Card.Header>
				<Button
					onClick={() => setOpen(!open)}
					aria-controls={"#manage_"+formData.id}
					aria-expanded={open}
					data-toggle="collapse"
					href={"#manage_"+formData.id}
					role="button"
				>
					{formData.name}
				</Button>
			</Card.Header>

			<Collapse in={open}>
				<Card.Body>
					<Box
						display="flex"
						marginLeft={-3}
						marginRight={-3}
						marginBottom={-3}
						marginTop={-3}
						wrap
						width="100%"
						direction="column"
						maxWidth={800}
					>
						<Box flex="grow" paddingX={3} paddingY={3}>
							<Box
								display="flex"
								wrap
								marginLeft={-3}
								marginRight={-3}
								marginBottom={-3}
								marginTop={-3}
							>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										label="Name"
										name="name"
										id="name"
										defaultValue={formData.name}
										value={formData.name}
										onChange={handleInputChange}
										placeholder={formData.name}
									/>
								</Box>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										disabled
										label="MAC"
										id="man"
										value={formData.mac}
									/>
								</Box>
							</Box>
						</Box>


						<Box flex="grow" paddingX={3} paddingY={3}>
							<Box
								display="flex"
								wrap
								marginLeft={-3}
								marginRight={-3}
								marginBottom={-3}
								marginTop={-3}
							>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										disabled
										label="Last seen"
										id="checkin_time"
										value={new Date(formData.checkin_time*1000)}
									/>
								</Box>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										disabled
										label="Next expected"
										id="device_next_init"
										value={new Date(formData.device_next_init*1000)}
									/>
								</Box>
							</Box>
						</Box>
						<Box flex="grow" paddingX={3} paddingY={3}>
							<Box
								display="flex"
								wrap
								marginLeft={-3}
								marginRight={-3}
								marginBottom={-3}
								marginTop={-3}
							>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										label="INIT_INTERVAL"
										name="INIT_INTERVAL"
										id="INIT_INTERVAL"
										defaultValue={formData.INIT_INTERVAL}
										value={formData.INIT_INTERVAL}
										onChange={handleInputChange}
										placeholder="Max time between INIT boots (wifi)"
									/>
								</Box>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										label="SLEEP_DURATION"
										name="SLEEP_DURATION"
										id="SLEEP_DURATION"
										defaultValue={formData.SLEEP_DURATION}
										value={formData.SLEEP_DURATION}
										onChange={handleInputChange}
										placeholder="Sleep time (sec)"
									/>
								</Box>
							</Box>
						</Box>



						<Box flex="grow" paddingX={3} paddingY={3}>
							<Box
								display="flex"
								wrap
								marginLeft={-3}
								marginRight={-3}
								marginBottom={-3}
								marginTop={-3}
							>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										label="MAX_ENTRYS_WITHOUT_INIT"
										name="MAX_ENTRYS_WITHOUT_INIT"
										id="MAX_ENTRYS_WITHOUT_INIT"
										defaultValue={formData.MAX_ENTRYS_WITHOUT_INIT}
										value={formData.MAX_ENTRYS_WITHOUT_INIT}
										onChange={handleInputChange}
										placeholder="Max boots before going to INIT"
									/>
								</Box>
								<Box flex="grow" paddingX={3} paddingY={3}>
									<TextField
										label="LIGHT"
										name="LIGHT"
										id="LIGHT"
										defaultValue={formData.LIGHT}
										value={formData.LIGHT}
										onChange={handleInputChange}
										placeholder="Light? 1/0"
									/>
								</Box>
							</Box>
						</Box>


	{/* 
						<Form.Group as={Row}>
							<Form.Label column sm={2}>Last sensor reading</Form.Label>
							<Col sm="5">
								<Form.Control
									type="text"
									readOnly
									defaultValue={formData.value}
									onChange={handleInputChange}/>
							</Col>
							<Col sm="5">
								<Form.Control
									type="text"
									readOnly
									defaultValue={formData.timestamp}
									onChange={handleInputChange}/>
							</Col>
						</Form.Group>

						<Form.Group as={Row}>
							<Form.Label column sm={2}>calibration_max</Form.Label>
							<Col sm="10">
								<Form.Control
									type="text"
									name="calibration_max"
									defaultValue={formData.calibration_max}
									onChange={handleInputChange}
									placeholder="10"
									aria-describedby="calibration_max_help"/>
								<Form.Text className="text-muted">Sensor calibration "wet" reading</Form.Text>
							</Col>
						</Form.Group>

						<Form.Group as={Row}>
							<Form.Label column sm={2}>calibration_min</Form.Label>
							<Col sm="10">
								<Form.Control
									type="text"
									name="calibration_min"
									defaultValue={formData.calibration_min}
									onChange={handleInputChange}
									placeholder="10"
									aria-describedby="calibration_min_help"/>
								<Form.Text className="text-muted">Sensor calibration "dry" reading</Form.Text>
							</Col>
						</Form.Group>

						<Form.Group as={Row}>
							<Form.Label column sm={2}>trigger_min</Form.Label>
							<Col sm="10">
								<Form.Control
									type="text"
									name="trigger_min"
									defaultValue={formData.trigger_min}
									onChange={handleInputChange}
									placeholder="10"
									aria-describedby="trigger_min_help"/>
								<Form.Text className="text-muted">Plant sensor trigger value for "I need water!"</Form.Text>
							</Col>
						</Form.Group>
	*/}

						<div onClick={SetLocation} >
						<Map
							devices={alldevices}
							activeDevice={device} />
						</div>

						<button
							onClick={() => SubmitConfig(formData)}
						>
							Submit
						</button>
					</Box>
				</Card.Body>
			</Collapse>
		</Card>

	);

}

export default ManagementPane;