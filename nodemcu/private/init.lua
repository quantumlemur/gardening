print("***** Booting init.  Setting startupcommand to INIT.")
node.startupcommand("@init.lua")

node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096) -- Change garbage collector settings

gpio.mode(4, gpio.OUTPUT)
gpio.write(4, 0) -- turn on LED

sec, usec, rate = rtctime.get()

local need_restart = false

tmr.softwd(50) -- 50 second restart if something hangs


if rtcfifo.ready() == 0 then -- prepare FIFO
	rtcfifo.prepare()
end


if file.exists("COMMON_DEFS.lua") then
	pcall(require, "COMMON_DEFS")
	pcall(rtcmem.write32, MEMSLOT_BOOTS_SINCE_INIT, 0)
end


-----------------------  COMPILATION  -----------------------


-- compile all .lua files to save on ram
local l = file.list(".\.lua");
for k,v in pairs(l) do
	if k ~= "init.lua" and not file.exists(string.gsub(k, "\.lua", "\.lc")) then
		if pcall(node.compile, k) then
		  -- no errors while running `foo'
		else
			print("INIT: COMPILATION FAILED.  FILE: "..k)
		  -- `foo' raised an error: take appropriate actions
		end
		
	end
end


-----------------------  WIFI  -----------------------


require("CREDENTIALS")

startup = function()
	if file.open("init.lua") == nil then
		print("INIT: init.lua deleted or renamed")
	else
		print("INIT: Running")
		http.get("http://192.168.86.33:5000/api/listfiles", "", check_for_updates)
	end
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
	print("INIT: Startup will resume momentarily, you have 3 seconds to abort.")
	print("INIT: Waiting...")
	tmr.create():alarm(3000, tmr.ALARM_SINGLE, startup)
end

wifi_disconnect_event = function(T)
	print('WIFI DISCONNECT EVENT '..T.reason)
	node.restart()
end


-----------------------  UPDATES  -----------------------


local update_fifo = (require "fifo").new()

get_file = function(filename)
	print("INIT: getting file "..filename)
	http.get("http://192.168.86.33:5000/api/getfile/"..filename, "", create_write_callback(filename))
end

create_write_callback = function(filename)
	return function(status_code, body, headers)
		if status_code == 200 then
			print("INIT: UPDATING FILE: "..filename)
			local filename_base = string.gsub(filename, "\.lua", "")

			file.remove(filename_base..".lc") -- delete the old .lc file, so it can be recreated on the next boot

			file.putcontents(filename, body)
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

	end
end

closeout = function()
	print("INIT: update cycle complete.")

	-- restart if updates downloaded, else move on to normal processing
	if need_restart then
		file.flush()
		print("INIT: restarting in 10 seconds...")
		tmr.create():alarm(10000, tmr.ALARM_SINGLE, function() node.restart() end)
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