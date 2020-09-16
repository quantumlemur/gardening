print("entering send_readings.lua")

history = {}

-- VOLTAGE

if CONFIG["state"]["voltage"] ~= 0 then
	table.insert(history, {sec, CONFIG["state"]["voltage"], neg_e, "volt"})
	CONFIG["state"]["voltage"] = 0
	
	local ok, json = pcall(sjson.encode, CONFIG)
	if ok then
		file.putcontents("CONFIG", json)
		file.flush()
		print(json)
	else
		print("failed to encode!")
	end
end

-- SENSORS

while rtcfifo.peek() do
	print("reading rtcfifo")
	local timestamp, value, neg_e, name = rtcfifo.pop()
	table.insert(history, {timestamp, value, neg_e, name})
	-- do something with the sample, e.g. upload to somewhere
end

handle_submission = function(status_code, body, headers)
	if status_code == 200 then
		print("readings sent successfully")
	else
		print("reading send failed")
	end
	print('disconnecting wifi')
	wifi.setmode(wifi.NULLMODE)
end

if table.getn(history) > 0 then
	print("sending history")
	local history_json = sjson.encode(history)
	http.post("http://nuc:5000/api/readings",
	"Content-Type: application/json\r\n", history_json, handle_submission)
else
	print("no history to send")
	print('disconnecting wifi')
	wifi.setmode(wifi.NULLMODE)
end