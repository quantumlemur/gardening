node.startupcommand("@init.lua")

-- Set server path here.  Be careful.
SERVER_URL = "http://nuc/"

node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096) -- Change garbage collector settings

gpio.mode(4, gpio.OUTPUT)
-- gpio.write(4, 0) -- turn on LED

local sec, usec, rate = rtctime.get()

local need_restart = false

tmr.softwd(50) -- 50 second restart if something hangs

if rtcfifo.ready() == 0 then -- prepare FIFO
	rtcfifo.prepare()
end

initialize_memory = function()
	rtcmem.write32(MEMSLOT_INITIALIZED, 0)
end

load_common_defs = function()
	require("COMMON_DEFS")
	rtcmem.write32(MEMSLOT_ENTRYS_SINCE_INIT, 0)
	rtcmem.write32(MEMSLOT_LAST_INIT_TIME, sec)
	rtcmem.write32(MEMSLOT_NEXT_INIT_TIME, sec + rtcmem.read32(MEMSLOT_INIT_INTERVAL))
	local light = rtcmem.read32(MEMSLOT_LIGHT)
	if light == 0 or light == 1 then
		gpio.write(4, 1 - rtcmem.read32(MEMSLOT_LIGHT))
	end
end
pcall(load_common_defs) -- protected call wrapper to catch errors


-----------------------  COMPILATION  -----------------------


-- compile all .lua files to save on ram
local l = file.list(".\.lua");
for k,v in pairs(l) do
	if k ~= "init.lua" and not file.exists(string.gsub(k, "\.lua", "\.lc")) then
		if pcall(node.compile, k) then
			-- no errors while running `foo'
			if k == "COMMON_DEFS.lua" then
				pcall(initialize_memory)
			end
		else
			print("INIT: COMPILATION FAILED.  FILE: "..k)
			-- `foo' raised an error: take appropriate actions
		end
		
	end
end


-----------------------  VOLTAGE  -----------------------


-- local sec, usec, rate = rtctime.get()

-- if sec > 0 then
-- 	local voltage = adc.readvdd33()

-- 	if voltage ~= 65535 then
-- 		-- we're in voltage mode
-- 		rtcfifo.put(sec, voltage, 0, "volt")
-- 		adc.force_init_mode(adc.INIT_ADC)
-- 		need_restart = true
-- 		print("INIT: read voltage of "..voltage)
-- 	end
-- else
-- 	print("INIT: didn't read voltage because t=0")
-- end


-----------------------  WIFI  -----------------------


require("CREDENTIALS")

startup = function()
	-- if file.open("init.lua") == nil then
	-- 	print("INIT: init.lua deleted or renamed")
	-- else
	-- 	print("INIT: Running")
		http.get(SERVER_URL.."/api/listfiles", "", check_for_updates)
	-- end
end

wifi_connect_event = function(T)
	print("INIT: Connection to AP("..T.SSID..") established!")
	print("INIT: Waiting for IP address...")
	-- if disconnect_ct ~= nil then disconnect_ct = nil end
end

wifi_got_ip_event = function(T)
	-- Note: Having an IP address does not mean there is internet access!
	-- Internet connectivity can be determined with net.dns.resolve().
	print("INIT: Wifi connection is ready! IP address is: "..T.IP)
	tmr.create():alarm(1000, tmr.ALARM_SINGLE, startup)
end

wifi_disconnect_event = function(T)
	print('WIFI DISCONNECT EVENT '..T.reason)
	node.restart()
end


-----------------------  UPDATES  -----------------------


local update_fifo = (require "fifo").new()

get_file = function(filename)
	http.get(SERVER_URL.."/api/getfile/"..filename, "", create_write_callback(filename))
end

create_write_callback = function(filename)
	return function(status_code, body, headers)
		if status_code == 200 then
			print("INIT: UPDATING FILE: "..filename)
			local filename_base = string.gsub(filename, "\.lua", "")

			file.remove(filename_base..".lc") -- delete the old .lc file, so it can be recreated on the next boot

			fd = file.open(filename, "w")
			if fd then
				fd:write(body)
				fd:close()
				if filename_base == "COMMON_DEFS" then
					pcall(initialize_memory)
				end
			else
				print("INIT:  WRITE FAILED FOR "..filename)
			end
		else
			print("INIT: FETCH FAILED FOR: "..filename)
		end
		-- try to process the next file in the queue, or if there is none, go to closeout()
		if not update_fifo:dequeue(get_file) then
			closeout()
		end
	end
end

file_is_changed = function(filename, hash)
	if file.exists(filename) then
		local device_hash = crypto.fhash("md5", filename)
		if encoder.toHex(device_hash) == hash then
			return false
		end
	end
	print("INIT: Change detected in "..filename)
	return true
end

check_for_updates = function(status_code, body, headers)
	if status_code == 200 then
		print("INIT: Update check got file list...")
		local decoder = sjson.decoder()
		decoder:write(body)
		local server_files = decoder:result()

		for key, file in pairs(server_files) do
			if file_is_changed(file[1], file[2]) then
				update_fifo:queue(file[1], get_file)
				need_restart = true
			end
		end

		-- try to process the next file in the queue, or if there is none, go to closeout()
		if not update_fifo:dequeue(get_file) then
			closeout()
		end
	else
		print("INIT: Update check failed.  http status code: "..status_code)

	end
end

closeout = function()
	print("INIT: update cycle complete.")

	-- restart if updates downloaded, else move on to normal processing
	if need_restart then
		print("INIT: restarting in 20 seconds...")
		tmr.create():alarm(20000, tmr.ALARM_SINGLE, function() node.restart() end)
	else
		if file.exists("entry.lua") then
			require("entry")
		end
	end
end


-----------------------  AND GO  -----------------------


-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("INIT: Connecting to WiFi access point...")
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