print("entering connect_wifi.lua")

-- sec, usec, rate = rtctime.get()
-- file.putcontents("next_wifi_time", sec + wifi_interval)
-- http.get("http://nuc:5000/status/wifi_connected", "", "")
-- http.get("http://nuc:5000/status/current_time1="..tostring(sec), "", "")
-- sntp.sync("129.6.15.28", callback, errorcallback, nil)
-- sec, usec, rate = rtctime.get()
-- http.get("http://nuc:5000/status/current_time2="..tostring(sec), "", "")

-- load credentials, 'SSID' and 'PASSWORD' declared and initialize in there
require("credentials")

-- callback = function(seconds, microseconds, server, info)
--   sec, usec, rate = rtctime.get()
--   -- http.get("http://nuc:5000/status/post_sync_time="..tostring(sec), "", "")
--   rtcmem.write32(RTCMEM_NEXTWIFI, sec + wifi_interval)
--   print("wifi successful.  next connection at "..rtcmem.read32(RTCMEM_NEXTWIFI))
--   -- file.putcontents("next_wifi_time", sec + wifi_interval)
--   tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() dofile("update_files.lua") end)
-- end

-- failcallback = function()
--   print("sync unsuccessful; turning off wifi")
--   wifi.setmode(wifi.NULLMODE)
-- end

function startup()
	if file.open("init.lua") == nil then
		print("init.lua deleted or renamed")
	else
		print("Running")
		file.close("init.lua")
		-- sec, usec, rate = rtctime.get()
		-- file.putcontents("next_wifi_time", sec + wifi_interval)
		-- http.get("http://nuc:5000/status/wifi_connected", "", "")
		-- http.get("http://nuc:5000/status/pre_sync_time="..tostring(sec), "", "")
		-- sntp.sync({"129.6.15.28", "132.163.97.1", "132.163.96.1", "128.138.140.44"}, callback, errorcallback, nil)
		sntp.sync("128.138.140.44", 
			function(seconds, microseconds, server, info)
				print("in sntp callback")
				sec, usec, rate = rtctime.get()
				-- http.get("http://nuc:5000/status/post_sync_time="..tostring(sec), "", "")
				CONFIG["state"]["last_wifi_time"] = sec
				CONFIG["state"]["next_wifi_time"] = sec + CONFIG["config"]["wifi_interval"]
				print('before')
				local ok, json = pcall(sjson.encode, CONFIG)
				if ok then
					file.putcontents("CONFIG", json)
					file.flush()
					print(json)
				else
					print("failed to encode!")
				end            -- file.putcontents("CONFIG", sjson.encode(CONFIG))
				print('after')
				print("wifi successful.  next connection at "..CONFIG["state"]["next_wifi_time"])
				-- file.putcontents("next_wifi_time", sec + wifi_interval)
				tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() require("update_files") end)
			end,
			function()
				print("sync unsuccessful; turning off wifi")
				wifi.setmode(wifi.NULLMODE)
			end,
			nil)
		-- dofile("update_files.lua")
		-- if file.exists("application.lua") then
		--   tmr.create():alarm(10000, tmr.ALARM_SINGLE, function() require("application") end)
		-- end
	end
end

-- Define WiFi station event callbacks
wifi_connect_event = function(T)
	print("Connection to AP("..T.SSID..") established!")
	print("Waiting for IP address...")
	-- if disconnect_ct ~= nil then disconnect_ct = nil end
end

wifi_got_ip_event = function(T)
	-- Note: Having an IP address does not mean there is internet access!
	-- Internet connectivity can be determined with net.dns.resolve().
	print("Wifi connection is ready! IP address is: "..T.IP)
	print("Startup will resume momentarily, you have 3 seconds to abort.")
	print("Waiting...")
	tmr.create():alarm(3000, tmr.ALARM_SINGLE, startup)
	wifi_connect_timer:unregister() -- disarm the connection timer
	-- wifi_connect_timer = nil
	tmr.create():alarm(30000, tmr.ALARM_SINGLE, go_to_sleep) -- activate the new sleep timer

end

wifi_disconnect_event = function(T)
	print('WIFI DISCONNECT EVENT '..T.reason)

	-- Voltage check timer, set the voltage read mode and restart
	-- if sec > CONFIG["state"]["next_voltage_check_time"] then
	-- 	adc.force_init_mode(adc.INIT_VDD33)
	-- 	node.restart()
	-- 	return
	-- end


	go_to_sleep()
	-- if T.reason == wifi.eventmon.reason.ASSOC_LEAVE then
	--   --the station has disassociated from a previously connected AP
	--   return
	-- end
	-- -- total_tries: how many times the station will attempt to connect to the AP. Should consider AP reboot duration.
	-- local total_tries = 75
	-- print("\nWiFi connection to AP("..T.SSID..") has failed!")

	-- --There are many possible disconnect reasons, the following iterates through
	-- --the list and returns the string corresponding to the disconnect reason.
	-- for key,val in pairs(wifi.eventmon.reason) do
	--   if val == T.reason then
	--     print("Disconnect reason: "..val.."("..key..")")
	--     break
	--   end
	-- end

	-- if disconnect_ct == nil then
	--   disconnect_ct = 1
	-- else
	--   disconnect_ct = disconnect_ct + 1
	-- end
	-- if disconnect_ct < total_tries then
	--   print("Retrying connection...(attempt "..(disconnect_ct+1).." of "..total_tries..")")
	-- else
	--   wifi.sta.disconnect()
	--   print("Aborting connection to AP!")
	--   disconnect_ct = nil
	--   go_to_sleep()
	-- end
end

-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("Connecting to WiFi access point...")
wifi.setmode(wifi.STATION)
wifi.sta.config({ssid=SSID, pwd=PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default