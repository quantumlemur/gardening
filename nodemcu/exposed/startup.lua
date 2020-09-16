


node.startupcommand("@init.lua")





-- compile all .lua files to save on ram
local l = file.list(".\.lua");
for k,v in pairs(l) do
	if not file.exists(string.gsub(k, "\.lua", "\.lc")) then
		node.compile(k)
	end
end

tmr.softwd(50) -- 50 second restart if something hangs


-- tmr.create():alarm(1000, tmr.ALARM_AUTO, function() print("heartbeat cpu: "..tostring(node.getcpufreq()).." heap: "..tostring(node.heap()).." time: "..tostring(rtctime.get())) end )
node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096)

sec, usec, rate = rtctime.get()
print("waking up at "..tostring(sec))


gpio.mode(4, gpio.OUTPUT)
gpio.write(4, 0)

if rtcfifo.ready() == 0 then
	rtcfifo.prepare()
end




-- read config
local config_file_contents = file.getcontents("CONFIG")
if config_file_contents ~= nil then
	-- local config_file_contents = file.getcontents("CONFIG")
	print(config_file_contents)
	CONFIG = sjson.decode(config_file_contents)
else
	CONFIG = {
		config = {
			wifi_interval = 60,
			sleep_interval = 10,
			voltage_check_interval = 300
		},
		state = {
			last_boot_time = 0,
			last_wifi_time = 0,
			next_wifi_time = 0,
			next_voltage_check_time = 0,
			voltage = 0
		}
	}
end

-- tmr.create():alarm(1000, tmr.ALARM_AUTO, function() print("heartbeat "..sjson.encode(CONFIG)) end)



-- check voltage and set ADC mode
local voltage = adc.readvdd33()
print("voltage: "..voltage)
if voltage ~= 65535 then
	-- if we're in voltage reading mode, take a reading and restart in ADC mode
	CONFIG["state"]["voltage"] = voltage
	CONFIG["state"]["next_voltage_check_time"] = CONFIG["state"]["next_voltage_check_time"] + CONFIG["config"]["voltage_check_interval"]
	local ok, json = pcall(sjson.encode, CONFIG)
	if ok then
		file.putcontents("CONFIG", json)
		file.flush()
		print(json)
	else
		print("failed to encode!")
	end
	
	adc.force_init_mode(adc.INIT_ADC)
	node.restart()
	return
end



print("last boot: "..CONFIG["state"]["last_boot_time"])
print("current time: "..sec)
print("next_wifi_time: "..CONFIG["state"]["next_wifi_time"])

CONFIG["state"]["last_boot_time"] = sec -- sec



if file.exists("update_files.new") then
	if file.exists("update_files.old") then
		file.remove("update_files.old")
	end
	file.rename("update_files.lua", "update_files.old")
	file.rename("update_files.new", "update_files.lua")
	file.flush()
end


-- re-write config changes and branch out to different files
local ok, json = pcall(sjson.encode, CONFIG)
if ok then
	file.putcontents("CONFIG", json)
	file.flush()
	print(json)
else
	print("failed to encode!")
end


-- if it's past time to connect to wifi, 
-- or rtc clock is 0
if (sec >= CONFIG['state']['next_wifi_time']) then
	-- wifi_in_use = true
	tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() require("connect_wifi") end )
end

-- read from the sensors
if file.exists("no_wifi.lua") then
	require("no_wifi")
end


go_to_sleep = function()
	sec, usec, rate = rtctime.get()
	print("going to sleep at "..tostring(sec))
	gpio.write(4, 1)
	tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() rtctime.dsleep(CONFIG["config"]["sleep_interval"]*1000000, 4) end )
	-- tmr.create():alarm(5000, tmr.ALARM_SINGLE, function() dofile("init.lua") end )
	print("...............at end of sleep function...")

	node.startupcommand("@startup.lua")
end


print("sleeping in 10 seconds if not connected...")
wifi_connect_timer = tmr.create()
wifi_connect_timer:alarm(20000, tmr.ALARM_SINGLE, go_to_sleep)

