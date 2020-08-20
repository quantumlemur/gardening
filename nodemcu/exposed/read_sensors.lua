print("entering read_sensors.lua")


sec, usec, rate = rtctime.get()

if sec > 0 then
	local value = adc.read(0)
	print("read value "..value)
	rtcfifo.put(sec, value, 0, "soil")
else
	print("didn't read because t=0")
end

go_to_sleep = function()
	sec, usec, rate = rtctime.get()
	print("going to sleep at "..tostring(sec))
	gpio.write(4, 1)
	tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() rtctime.dsleep(sleep_interval*1000000, 4) end )
	-- tmr.create():alarm(5000, tmr.ALARM_SINGLE, function() dofile("init.lua") end )
	print("...............at end of sleep function...")
end


print(tostring(wifi.getmode()).." "..wifi.NULLMODE)
if wifi.getmode() == wifi.NULLMODE then
	print("done with sensors and wifi is off.  going to sleep")
	go_to_sleep()
end