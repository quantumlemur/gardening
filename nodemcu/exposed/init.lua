-- compile all .lua files to save on ram
local l = file.list(".\.lua");
for k,v in pairs(l) do
	if not file.exists(string.gsub(k, "\.lua", "\.lc")) then
		node.compile(k)
	end
end


-- RTC Memoryslot constants
RTCMEM_LASTBOOT = 21
RTCMEM_NEXTWIFI = 22


tmr.softwd(50) -- 50 second restart if something hangs


tmr.create():alarm(1000, tmr.ALARM_AUTO, function() print("heartbeat cpu: "..tostring(node.getcpufreq()).." heap: "..tostring(node.heap()).." time: "..tostring(rtctime.get())) end )
node.egc.setmode(node.egc.ON_MEM_LIMIT, -6096)

sec, usec, rate = rtctime.get()
print("waking up at "..tostring(sec))


gpio.mode(4, gpio.OUTPUT)
gpio.write(4, 0)

if rtcfifo.ready() == 0 then
	rtcfifo.prepare()
end

if sec == 0 then
	rtcmem.write32(RTCMEM_LASTBOOT, 0)
	rtcmem.write32(RTCMEM_NEXTWIFI, 0)
end


-- ensure DAC is set to read external voltage
if adc.force_init_mode(adc.INIT_ADC) then
	node.restart()
	return -- don't bother continuing, the restart is scheduled
end


if not file.exists("wifi_interval") then
	file.putcontents("wifi_interval", 60) -- seconds
end

if not file.exists("sleep_interval") then
	file.putcontents("sleep_interval", 10) -- seconds
end


last_boot_time = rtcmem.read32(RTCMEM_LASTBOOT)
next_wifi_time = rtcmem.read32(RTCMEM_NEXTWIFI)
print("last boot: "..last_boot_time)
print("current time: "..sec)
print("next_wifi_time: "..next_wifi_time)
wifi_interval = tonumber(file.getcontents("wifi_interval"))
sleep_interval = tonumber(file.getcontents("sleep_interval"))


if file.exists("update_files.new") then
	if file.exists("update_files.old") then
		file.remove("update_files.old")
	end
	file.rename("update_files.lua", "update_files.old")
	file.rename("update_files.new", "update_files.lua")
	file.flush()
end

-- if it's past time to connect to wifi, 
-- or rtc clock is 0
if (sec >= next_wifi_time) then
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
	tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() rtctime.dsleep(sleep_interval*1000000, 4) end )
	-- tmr.create():alarm(5000, tmr.ALARM_SINGLE, function() dofile("init.lua") end )
	print("...............at end of sleep function...")
end


print("sleeping in 10 seconds if not connected...")
wifi_connect_timer = tmr.create()
wifi_connect_timer:alarm(10000, tmr.ALARM_SINGLE, go_to_sleep)

