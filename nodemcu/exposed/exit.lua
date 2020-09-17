



sec, usec, rate = rtctime.get()
print("EXIT: going to sleep in 10 seconds at "..tostring(sec))
gpio.write(4, 1)
tmr.create():alarm(10000, tmr.ALARM_SINGLE, function() rtctime.dsleep(CONFIG["sleep_interval"]*1000000, 4) end )



if rtcmem.read32(MEMSLOT_BOOTS_SINCE_INIT) > 2 then
	print("***** Exit finished successfully, but booted 10 times without init.  Setting startupcommand to INIT.")
	node.startupcommand("@init.lua")
else
	print("***** Exit finished successfully.  Setting startupcommand to ENTRY.")
	node.startupcommand("if file.exists('entry.lua') then require('entry') else require('init') end")
end

