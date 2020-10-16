

require("CREDENTIALS")

node.startupcommand("@init.lua")

node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096) -- Change garbage collector settings

gpio.mode(4, gpio.OUTPUT)
-- gpio.write(4, 0) -- turn on LED

local sec, usec, rate = rtctime.get()

local need_restart = false

tmr.softwd(50) -- 50 second restart if something hangs

if rtcfifo.ready() == 0 then -- prepare FIFO
	rtcfifo.prepare()
end

local initialize_memory, load_common_defs, get_file, create_write_callback, file_is_changed, check_for_updates, closeout, delete_files

initialize_memory = function()
	rtcmem.write32(MEMSLOT_INITIALIZED, 0)
end

oad_common_defs = function()
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
	if k ~= "init.lua" and k ~= "CREDENTIALS.lua" and not file.exists(string.gsub(k, "\.lua", "\.lc")) then
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

local function startup()
	-- if file.open("init.lua") == nil then
	-- 	print("INIT: init.lua deleted or renamed")
	-- else
	-- 	print("INIT: Running")
	print("INIT: Fetching list of files from "..SERVER_URL)
	http.get(SERVER_URL.."/listfiles", "", check_for_updates)
	-- end
end

local function wifi_connect_event(T)
	print("INIT: Connection to AP("..T.SSID..") established!")
	print("INIT: Waiting for IP address...")
	-- if disconnect_ct ~= nil then disconnect_ct = nil end
end

local function wifi_got_ip_event(T)
	-- Note: Having an IP address does not mean there is internet access!
	-- Internet connectivity can be determined with net.dns.resolve().
	print("INIT: Wifi connection is ready! IP address is: "..T.IP)
	tmr.create():alarm(1000, tmr.ALARM_SINGLE, startup)
end

local function wifi_disconnect_event(T)
	print('WIFI DISCONNECT EVENT '..T.reason)
	node.restart()
end


-----------------------  UPDATES  -----------------------


local update_fifo = (require "fifo").new()

get_file = function(filename)
	http.get(SERVER_URL.."/getfile/"..filename, "", create_write_callback(filename))
end

create_write_callback = function(filename)
	print("INIT: in create_write_callback")
	return function(status_code, body, headers)
		if status_code == 200 then
			print("INIT: UPDATING FILE: "..filename)
			local filename_base = string.gsub(filename, "\.lua", "")

			file.remove(filename_base..".lc") -- delete the old .lc file, so it can be recreated on the next boot

			fd = file.open(filename, "w")
			if fd then
				fd:write(body)
				fd:close(); fd=nil
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
			print("INIT: end, inside callback")
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
	print("INIT: in check_for_updates")
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
		if need_restart then
			update_fifo:dequeue(get_file)
		else
			print("INIT: end, outside callback")
			closeout()
		end
	else
		print("INIT: Update check failed.  http status code: "..status_code)
	end
end

closeout = function()
	print("INIT: update cycle complete.  Checking for disallowed files...")

	if file.exists("ALLOWED_FILES.cfg") then
		local fd_allowed = file.open("ALLOWED_FILES.cfg")
		if fd_allowed then
			local allowed_file_list = fd_allowed.read()
			fd_allowed.close(); fd_allowed = nil
		
			local l = file.list();
			for k,v in pairs(l) do
				if not string.find(allowed_file_list, k) then
					print("INIT: DELETING FILE "..k)
					file.remove(k)
				end
			end
		end
	end

	-- restart if updates downloaded, else move on to normal processing
	if need_restart then
		print("INIT: restarting in 10 seconds...")
		tmr.create():alarm(10000, tmr.ALARM_SINGLE, function() node.restart() end)
	else
		if file.exists("entry.lua") then
			initialize_memory = nil
			load_common_defs = nil
			get_file = nil
			create_write_callback = nil
			file_is_changed = nil
			check_for_updates = nil
			closeout = nil
			delete_files = nil
			require("entry")
		end
	end
end


-----------------------  DELETE FILES  -----------------------

delete_files = function()
	if file.exists("ALLOWED_FILES.cfg") then
		local fd_allowed = file.open("ALLOWED_FILES.cfg")
		if fd_allowed then
			local allowed_file_list = fd_allowed.read()
			fd_allowed.close(); fd_allowed = nil
		
			local l = file.list();
			for k,v in pairs(l) do
				if not strfind(allowed_file_list, k) then
					print("INIT: DELETING FILE "..k)
				end
			end
		end
	end
end


-----------------------  AND GO  -----------------------


-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("INIT: Connecting to WiFi access point...")
wifi.setmode(wifi.STATION, false)
wifi.sta.config({ssid=SSID, pwd=PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default