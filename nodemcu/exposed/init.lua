node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096)

gpio.mode(4, gpio.OUTPUT)
gpio.write(4, 0)

require("credentials")


startup = function()
	if file.open("init.lua") == nil then
		print("init.lua deleted or renamed")
	else
		print("Running")
		file.close("init.lua")
		http.get("http://192.168.86.33:5000/api/listfiles", "", check_for_updates)
	end
end


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
end


wifi_disconnect_event = function(T)
	print('WIFI DISCONNECT EVENT '..T.reason)
	node.restart()
end


create_write_callback = function(filename, files_to_update)
	print("creating callback for "..filename)
	return function(status_code, body, headers)
		print("in callback for "..filename)
		if status_code == 200 then
			print("  updating "..filename)
			local filename_base = string.gsub(filename, "\.lua", "")

			file.remove(filename_base..".lc")
			print(body)

			file.putcontents(filename, body)
			if file.exists(filename_base..".lua") then
				node.compile(filename_base..".lua")
			end
			
		end
		if files_to_update == nil then
			file.flush()
			print("file update complete.  Restarting...")
			tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() node.restart() end )
		else
			local next_filename, next_files_to_update = table.remove(files_to_update)
			http.get("http://192.168.86.33:5000/api/getfile/"..next_filename, "", create_write_callback(next_filename, next_files_to_update))
		end
	end
end


file_is_changed = function(filename, hash)
	print("testing for file change on "..filename.." with hash "..hash)
	if file.exists(filename) then
		local device_hash = crypto.fhash("md5", filename)
		if encoder.toHex(device_hash) == hash then
			return false
		end
	end
	return true
end


check_for_updates = function(status_code, body, headers)
local files_to_update = {}
	if status_code == 200 then
		local decoder = sjson.decoder()
		decoder:write(body)
		local server_files = decoder:result()

		for key, file in pairs(server_files) do
			if file_is_changed(file[1], file[2]) then
				table.insert(files_to_update, file[1])
			end
		end
		if next(files_to_update) == nil then
			print("No files to update.  Restarting in 20 seconds...")
			file.remove("UPDATE_IN_PROGRESS")
			file.flush()
			tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() node.restart() end)
		else
			print("downloading new files...")
			local next_filename, next_files_to_update = table.remove(files_to_update)
			http.get("http://192.168.86.33:5000/api/getfile/"..next_filename, "", create_write_callback(next_filename, next_files_to_update))
		end
	end
end


-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("Connecting to WiFi access point...")
wifi.setmode(wifi.STATION)
wifi.sta.config({ssid=SSID, pwd=PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default