import React, { useState } from "react";
import "gestalt/dist/gestalt.css";

import 'bootstrap/dist/css/bootstrap.css';
import { Button, Card, Col, Collapse, Form, Row } from 'react-bootstrap';

import { Box, Heading, Text } from "gestalt";



function SubmitConfig(data) {
	
	const requestOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(data)
	};
	fetch("/api/submit_config", requestOptions)

}


function ManagementPane({device}) {

	const [open, setOpen] = useState(false);
	const [formData, setFormData] = useState(device)

	function handleInputChange(event) {
    const target = event.target;
    const value = target.value;
		const name = target.name;

		// this is DEFINITELY not the right way to do this.  omg.
		const newFormData = formData;
		formData[name] = value;

		setFormData(newFormData);

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

					<Form.Group as={Row}>
						<Form.Label column sm={2}>Name</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								defaultValue={formData.name}
								onChange={handleInputChange}
								placeholder={formData.name}/>
						</Col>
					</Form.Group>

					<Form.Group as={Row}>
						<Form.Label column sm={2}>mac address</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								readOnly
								name="mac"
								value={formData.mac}/>
						</Col>
					</Form.Group>

					<Form.Group as={Row}>
						<Form.Label column sm={2}>Last seen</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								readOnly
								name="checkin_time"
								value={new Date(formData.checkin_time*1000)}/>
						</Col>
					</Form.Group>

					<Form.Group as={Row}>
						<Form.Label column sm={2}>INIT_INTERVAL</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								name="INIT_INTERVAL"
								defaultValue={formData.INIT_INTERVAL}
								onChange={handleInputChange}
								placeholder="1"
								aria-describedby="INIT_INTERVAL_help"/>
							<Form.Text className="text-muted">Maximum amount of time (seconds) between INIT boots and connecting to wifi.</Form.Text>
						</Col>
					</Form.Group>

					<Form.Group as={Row}>
						<Form.Label column sm={2}>SLEEP_DURATION</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								name="SLEEP_DURATION"
								defaultValue={formData.SLEEP_DURATION}
								onChange={handleInputChange}
								placeholder="1"
								aria-describedby="SLEEP_DURAION_help"/>
							<Form.Text className="text-muted">How long to sleep (seconds) between wakeups (and sensor readings).</Form.Text>
						</Col>
					</Form.Group>

					<Form.Group as={Row}>
						<Form.Label column sm={2}>SLEEP_DELAY</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								name="SLEEP_DELAY"
								defaultValue={formData.SLEEP_DELAY}
								onChange={handleInputChange}
								placeholder="10"
								aria-describedby="SLEEP_DELAY_help"/>
							<Form.Text className="text-muted">How long to wait at the end of a cycle before going back to sleep.  Must be long enough to allow all actions (including http requests) to complete.</Form.Text>
						</Col>
					</Form.Group>

					<Form.Group as={Row}>
						<Form.Label column sm={2}>LIGHT</Form.Label>
						<Col sm="10">
							<Form.Control
								type="text"
								name="LIGHT"
								defaultValue={formData.LIGHT}
								onChange={handleInputChange}
								placeholder="10"
								aria-describedby="LIGHT_help"/>
							<Form.Text className="text-muted">Turn on the LED while awake?  1 or 0.</Form.Text>
						</Col>
					</Form.Group>


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

					<button
						onClick={() => SubmitConfig(formData)}
					>
						Submit
					</button>

				</Card.Body>
			</Collapse>
		</Card>

	);

}

export default ManagementPane;