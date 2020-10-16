

local function update_next_init_expected()
	local sec, usec, rate = rtctime.get()
	local next_init_by_time = rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)
	local next_init_by_count = sec + ((rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT) - rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT)) * rtcmem.read32(MEMSLOT_SLEEP_DURATION))
	rtcmem.write32(MEMSLOT_NEXT_INIT_EXPECTED, math.min(next_init_by_time, next_init_by_count))
end


local function parse_config(status_code, body, headers)
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
	update_next_init_expected()
	-- send_readings()
end

return {
	{
		name = "getting config",
		type = "get",
		url = SERVER_URL.."/config",
		callback = parse_config
	}
}