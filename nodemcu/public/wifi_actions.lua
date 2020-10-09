print("WIFI_ACTIONS: entering wifi_actions.lua")


-----------------------  SEND LOG  -----------------------


send_log = function()
	if logfile_to_send then
		local contents = logfile_to_send:read()
		if contents ~= nil then
			uart.write(0,"WIFI_ACTIONS: Sending a bit of the log\r\n")
			http.post(SERVER_URL.."/log",
				"mac: "..wifi.sta.getmac().."\r\ndevice-next-init: "..next_init_expected.."\r\nContent-Type: application/json\r\n",
				contents,
				send_log
				)
		else
			logfile_to_send:close()
			print("WIFI_ACTIONS: end of send_log, going to fetch_config")
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


-----------------------  SEND READINGS  -----------------------


send_readings = function()
	local history = {}

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
		send_log() -- move up to send_log()
	end

	if table.getn(history) > 0 then
		print("WIFI_ACTIONS: sending history")
		local history_json = sjson.encode(history)
		http.post(SERVER_URL.."/readings",
			"mac: "..wifi.sta.getmac().."\r\ndevice-next-init: "..next_init_expected.."\r\nContent-Type: application/json\r\n",
			history_json,
			handle_submission)
	else
		print("WIFI_ACTIONS: no history to send")
		send_log() -- move up to send_log()
	end
end


-----------------------  GET CONFIG  -----------------------

calc_next_init_expected = function()
	local sec, usec, rate = rtctime.get()
	local next_init_by_time = rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)
	local next_init_by_count = sec + ((rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT) - rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT)) * rtcmem.read32(MEMSLOT_SLEEP_DURATION))
	return math.min(next_init_by_time, next_init_by_count)
end


parse_config = function(status_code, body, headers)
	print("WIFI_ACTIONS: in parse_config")

	if status_code == 200 then
		local decoder = sjson.decoder()
		decoder:write(body)
		local device_config = decoder:result()
		print("WIFI_ACTIONS: "..body)
		print("WIFI_ACTIONS: CONFIG: INIT_INTERVAL: "..device_config["INIT_INTERVAL"])
		print("WIFI_ACTIONS: CONFIG: SLEEP_DURATION: "..device_config["SLEEP_DURATION"])
		-- print("WIFI_ACTIONS: CONFIG: SLEEP_DELAY: "..device_config["SLEEP_DELAY"])
		print("WIFI_ACTIONS: CONFIG: MAX_ENTRYS_WITHOUT_INIT: "..device_config["MAX_ENTRYS_WITHOUT_INIT"])
		print("WIFI_ACTIONS: CONFIG: LIGHT: "..device_config["LIGHT"])

		if device_config["INIT_INTERVAL"] ~= nil then rtcmem.write32(MEMSLOT_INIT_INTERVAL, device_config["INIT_INTERVAL"]) end
		if device_config["SLEEP_DURATION"] ~= nil then rtcmem.write32(MEMSLOT_SLEEP_DURATION, device_config["SLEEP_DURATION"]) end
		-- if device_config["SLEEP_DELAY"] ~= nil then rtcmem.write32(MEMSLOT_SLEEP_DELAY, device_config["SLEEP_DELAY"]) end
		if device_config["MAX_ENTRYS_WITHOUT_INIT"] ~= nil then rtcmem.write32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT, device_config["MAX_ENTRYS_WITHOUT_INIT"]) end
		if device_config["LIGHT"] ~= nil then rtcmem.write32(MEMSLOT_LIGHT, device_config["LIGHT"]) end
		

		-- update the next boot time, in case the config has changed
		local sec, usec, rate = rtctime.get()
		rtcmem.write32(MEMSLOT_NEXT_INIT_TIME, sec + rtcmem.read32(MEMSLOT_INIT_INTERVAL))
	end
	next_init_expected = calc_next_init_expected()
	send_readings()
end

fetch_config = function()
	print("WIFI_ACTIONS: in fetch_config")
	next_init_expected = calc_next_init_expected()
	http.get(SERVER_URL.."/config",
		"mac: "..wifi.sta.getmac().."\r\ndevice-next-init: "..next_init_expected.."\r\nContent-Type: application/json\r\n",
		parse_config
		)
end


-----------------------  SNTP  -----------------------


sntp.sync("128.138.140.44", 
	function(seconds, microseconds, server, info)
		local sec, usec, rate = rtctime.get()
		-- rtcmem.write32(MEMSLOT_LAST_WIFI_TIME, sec)
		print("WIFI_ACTIONS: SNTP sync successful. Time: "..format_time(sec))
		fetch_config()
	end,
	function()
		print("WIFI_ACTIONS: SNTP sync unsuccessful. Time: "..format_time(sec))
		fetch_config()
	end,
	nil)