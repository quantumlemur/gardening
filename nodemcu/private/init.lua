-- RTC memory slots
LAST_BOOT_TIME = 21
LAST_WIFI_TIME = 22
NEXT_WIFI_TIME = 23
NEXT_VOLTAGE_CHECK_TIME = 24
VOLTAGE = 25




node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096) -- Change garbage collector settings

gpio.mode(4, gpio.OUTPUT)
gpio.write(4, 0) -- turn on LED

sec, usec, rate = rtctime.get()



-----------------------  COMPILATION  -----------------------


-- compile all .lua files to save on ram
local l = file.list(".\.lua");
for k,v in pairs(l) do
	if k ~= "init.lua" and not file.exists(string.gsub(k, "\.lua", "\.lc")) then
		node.compile(k)
	end
end


-----------------------  CONFIG  -----------------------



-- read config
local config_file_contents = file.getcontents("CONFIG")
if config_file_contents ~= nil then
	-- local config_file_contents = file.getcontents("CONFIG")
	print(config_file_contents)
	CONFIG = sjson.decode(config_file_contents)
else
	CONFIG = {
		wifi_interval = 60,
		sleep_interval = 10,
		voltage_check_interval = 300
	}
end


-----------------------  VOLTAGE  -----------------------


-- check voltage and set ADC mode
local voltage = adc.readvdd33()
print("voltage: "..voltage)
if voltage ~= 65535 then
	-- if we're in voltage reading mode, take a reading and restart in ADC mode
	rtcmem.write32(VOLTAGE, voltage)
	local next_voltage_check_time = sec + CONFIG["voltage_check_interval"]
	rtcmem.write32(NEXT_VOLTAGE_CHECK_TIME, next_voltage_check_time)
	
	adc.force_init_mode(adc.INIT_ADC)
end


-----------------------  WIFI  -----------------------


require("CREDENTIALS")

startup = function()
	if file.open("init.lua") == nil then
		print("init.lua deleted or renamed")
	else
		print("Running")
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


-----------------------  UPDATES  -----------------------


local update_fifo = (require "fifo").new()

get_file = function(filename)
	print("getting file "..filename)
	http.get("http://192.168.86.33:5000/api/getfile/"..filename, "", create_write_callback(filename))
end

create_write_callback = function(filename)
	print("creating callback for "..filename)
	return function(status_code, body, headers)
		print("in callback for "..filename)
		if status_code == 200 then
			print("  updating "..filename)
			local filename_base = string.gsub(filename, "\.lua", "")

			file.remove(filename_base..".lc")

			file.putcontents(filename, body)
			
		end
		-- process the next file in the queue
		update_fifo:dequeue(get_file)
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
	local need_restart = false
	if status_code == 200 then
		local decoder = sjson.decoder()
		decoder:write(body)
		local server_files = decoder:result()

		for key, file in pairs(server_files) do
			if file_is_changed(file[1], file[2]) then
				print("file is changed... "..file[1].." "..file[2])
				update_fifo:queue(file[1], get_file)
				print("file queued.. "..file[1])
				need_restart = true
			end
		end

		print("end of queueing files")

		update_fifo:dequeue(get_file)
		-- I think we'll end up here after the queue is done processing
		if need_restart then
			file.flush()
		end

		-- restart if voltage read or updates downloaded, else move on to normal processing
		if (rtcmem.read32(VOLTAGE) ~= -1) or need_restart then
			tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() node.restart() end)
		else
			if file.exists("main.lua") then
				require("main")
			end
		end
	end
end


-----------------------  AND GO  -----------------------


-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("Connecting to WiFi access point...")
wifi.setmode(wifi.STATION)
wifi.sta.config({ssid=SSID, pwd=PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default


-- Files available to compile?
-- 		Y: We're in update cycle.  Compile files.
-- 	In voltage read mode?
-- 		Y:	Read + store voltage.
-- 			Set ADC mode.
-- 			Set voltage-read flag
-- 	Connect to wifi
-- 	Updates available?
-- 		Y:	Download updates
-- 			Set restart timer.  Restart
-- 		N:	Was voltage read?
-- 				Y:	Set restart timer.  Restart.
-- 				N:	Run Main