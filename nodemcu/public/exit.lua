

local sleep_delay = 10 -- seconds, to wait for all actions to finish before going to sleep

local sec, usec, rate = rtctime.get()

local sleep_duration = math.min(rtcmem.read32(MEMSLOT_SLEEP_DURATION), rtcmem.read32(MEMSLOT_NEXT_INIT_TIME) - sec)
sleep_duration = math.max(sleep_duration, 1)

if DEBUG ~= nil then
	print("EXIT: DEBUG: staying awake and going to sleep in  "..(sleep_delay + sleep_duration).." seconds for 1 second.")
	gpio.write(4, 1)
	tmr.create():alarm((sleep_delay + sleep_duration)*1000,
		tmr.ALARM_SINGLE,
		function()
			if logfile then
				logfile:close()
				logfile = nil
			end
			rtctime.dsleep(1*1000000, 4)
		end
	)
else
	print("EXIT: going to sleep in "..sleep_delay.." seconds for "..sleep_duration.." seconds.")
	gpio.write(4, 1)
	tmr.create():alarm(sleep_delay*1000,
		tmr.ALARM_SINGLE,
		function()
			if logfile then
				logfile:close()
				logfile = nil
			end
			rtctime.dsleep(sleep_duration*1000000, 4)
		end
	)
end




if sec == 0 or (sec + rtcmem.read32(MEMSLOT_SLEEP_DURATION) >= rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)) or rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT) >= rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT) then
	print("*** timer: "..tostring(sec >= rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)).." maxcount: "..tostring(rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT) >= rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT)))
	print("** timer: "..sec.." of "..rtcmem.read32(MEMSLOT_NEXT_INIT_TIME))
	print("** count: "..rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT).." of "..rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT))
	print("***** Exit finished successfully, but time to INIT.  Setting startupcommand to INIT.")
	adc.force_init_mode(adc.INIT_VDD33) -- set it to take a voltage reading next boot
	node.startupcommand("@init.lua")
else
	print("***** Exit finished successfully.  Setting startupcommand to ENTRY.")
	node.startupcommand("if file.exists('entry.lua') then require('entry') else require('init') end")
end

