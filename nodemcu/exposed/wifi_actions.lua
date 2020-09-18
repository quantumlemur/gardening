print("WIFI_ACTIONS: entering wifi_actions.lua")


-----------------------  SNTP  -----------------------


sntp.sync("128.138.140.44", 
	function(seconds, microseconds, server, info)
		local sec, usec, rate = rtctime.get()
		-- rtcmem.write32(MEMSLOT_LAST_WIFI_TIME, sec)
		print("WIFI_ACTIONS: SNTP sync successful. Time: "..format_time(sec))
	end,
	function()
		print("WIFI_ACTIONS: SNTP sync unsuccessful. Time: "..format_time(sec))
	end,
	nil)


-----------------------  SEND READINGS  -----------------------


history = {}

while rtcfifo.peek() do
	print("WIFI_ACTIONS: reading rtcfifo")
	local timestamp, value, neg_e, name = rtcfifo.pop()
	table.insert(history, {timestamp, value, neg_e, name})
end

handle_submission = function(status_code, body, headers)
	if status_code == 200 then
		print("WIFI_ACTIONS: readings sent successfully")
	else
		print("WIFI_ACTIONS: reading send failed")
	end
end

if table.getn(history) > 0 then
	print("WIFI_ACTIONS: sending history")
	local history_json = sjson.encode(history)
	http.post("http://nuc:5000/api/readings",
		"mac: "..wifi.sta.getmac().."\r\nContent-Type: application/json\r\n",
		history_json,
		handle_submission)
else
	print("WIFI_ACTIONS: no history to send")
end


-----------------------  SEND LOG  -----------------------


send_log = function()
	if logfile_to_send then
		local contents = logfile_to_send:read()
		if contents ~= nil then
			uart.write(0,"WIFI_ACTIONS: Sending a bit of the log\r\n")
			http.post("http://nuc:5000/api/log",
				"mac: "..wifi.sta.getmac().."\r\n",
				contents,
				send_log)
		else
			logfile_to_send:close()
		end
	end
end


if logfile then
	logfile:close()
	file.remove("logfile_to_send")
	local success = file.rename("logfile", "logfile_to_send")
	logfile = file.open("logfile", "w")
	logfile_to_send = file.open("logfile_to_send", "r")
	print("WIFI_ACTIONS: log copy success: "..tostring(success))
end
send_log()