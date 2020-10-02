



local sec, usec, rate = rtctime.get()

local sleep_delay = math.min(rtcmem.read32(MEMSLOT_SLEEP_DELAY), rtcmem.read32(MEMSLOT_NEXT_INIT_TIME) - sec)

print("EXIT: going to sleep in "..sleep_delay.." seconds for "..rtcmem.read32(MEMSLOT_SLEEP_DURATION).." seconds.")
gpio.write(4, 1)
tmr.create():alarm(rtcmem.read32(MEMSLOT_SLEEP_DELAY)*1000,
	tmr.ALARM_SINGLE,
	function()
		if logfile then
			logfile:close()
			logfile = nil
		end
		rtctime.dsleep(sleep_delay*1000000, 4)
	end
	)



if sec == 0 or (sec + rtcmem.read32(MEMSLOT_SLEEP_DELAY) >= rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)) or rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT) >= rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT) then
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

