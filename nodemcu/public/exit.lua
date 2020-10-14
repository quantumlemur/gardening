

local sec, usec, rate = rtctime.get()
local sleep_delay = 10
local sleep_duration = 10


if wifi.getmode() == wifi.STATION then
	-- long delay but quick duration if we are connected, to restart and read the soil sensor
	sleep_delay = 10 -- seconds, to wait for all actions to finish before going to sleep
	sleep_duration = 1
	print("EXIT: Brief sleep and restart because wifi is connected.")
else
	-- initiate sleep quickly if we're not connected (don't need to wait for wifi callbacks)
	sleep_delay = 1
	sleep_duration = math.min(rtcmem.read32(MEMSLOT_SLEEP_DURATION), rtcmem.read32(MEMSLOT_NEXT_INIT_TIME) - sec)
	sleep_duration = math.max(sleep_duration, 1)
	print("EXIT: Normal sleep timing calcs because wifi isn't connected.")
end


if DEBUG then
	print("EXIT: DEBUG MODE.  NOT SLEEPING.")
	sleep_delay = sleep_duration + sleep_delay
	sleep_duration = 1
end


local startupcommand = "@init.lua"

if sec == 0 then
	print("*** Setting startupcommand to init.  Reason: clock at 0")
elseif sec + rtcmem.read32(MEMSLOT_SLEEP_DURATION) >= rtcmem.read32(MEMSLOT_NEXT_INIT_TIME) then
	print("*** Setting startupcommand to init.  Reason: next sleep would pass the next init time.")
	print("*** Sleep time: "..rtcmem.read32(MEMSLOT_SLEEP_DURATION).." Time to next init: "..(rtcmem.read32(MEMSLOT_NEXT_INIT_TIME) - sec) )
elseif rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT) >= rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT) then
	print("*** Setting startupcommand to init.  Reason: max num non-init boots reached.")
	print("*** Entry "..rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT).." of "..rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT))
else
	print("*** Setting startupcommand to entry.")
	startupcommand = "if file.exists('entry.lua') then require('entry') else require('init') end"
end

-- 	print("*** timer: "..tostring(sec >= rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)).." maxcount: "..tostring(rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT) >= rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT)))
-- 	print("** timer: "..sec.." of "..rtcmem.read32(MEMSLOT_NEXT_INIT_TIME))
-- 	print("** count: "..rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT).." of "..rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT))
-- 	print("***** Exit finished successfully, but time to INIT.  Setting startupcommand to INIT.")
-- 	node.startupcommand("@init.lua")
-- else
-- 	print("***** Exit finished successfully.  Setting startupcommand to ENTRY.")
-- 	node.startupcommand("if file.exists('entry.lua') then require('entry') else require('init') end")
-- end


print("EXIT: going to sleep in "..sleep_delay.." seconds for "..sleep_duration.." seconds.")
gpio.write(4, 1)
tmr.create():alarm(sleep_delay*1000,
	tmr.ALARM_SINGLE,
	function()
	if logfile then
		logfile:close()
		logfile = nil
	end
	wifi.setmode(wifi.NULLMODE, true)
	if startupcommand == "@init.lua" then
		adc.force_init_mode(adc.INIT_VDD33) -- set it to take a voltage reading next boot
	end
	node.startupcommand(startupcommand)
	rtctime.dsleep(sleep_duration*1000000, 4)
	end
)