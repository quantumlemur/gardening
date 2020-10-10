print("READ_SENSORS: entering read_sensors.lua")


local sec, usec, rate = rtctime.get()

if sec > 0 then
	local voltage = adc.readvdd33()
	local adcval = adc.read(0)

	if voltage ~= 65535 then
		-- we're in voltage mode
		print("READ_SENSORS: read voltage")
		rtcfifo.put(sec, voltage, 0, "volt")
		adc.force_init_mode(adc.INIT_ADC)
	else
		-- we're in ADC mode
		print("READ_SENSORS: read soil sensor")
		rtcfifo.put(sec, adcval, 0, "soil")
	end

	-- read DHT22 temp and humidity
	local status, temp, humi, temp_dec, humi_dec = dht.read(DHT_PIN)
	if status == dht.OK then
		rtcfifo.put(sec, math.floor(temp), 0, "temp")
		rtcfifo.put(sec, math.floor(humi), 0, "humi")
	elseif status == dht.ERROR_CHECKSUM then
		print( "DHT Checksum error." )
	elseif status == dht.ERROR_TIMEOUT then
		print( "DHT timed out." )
	end
	
else
	print("READ_SENSORS: didn't read because t=0")
end




-- go_to_sleep = function()
-- 	sec, usec, rate = rtctime.get()
-- 	print("going to sleep at "..tostring(sec))
-- 	gpio.write(4, 1)
-- 	tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() rtctime.dsleep(sleep_interval*1000000, 4) end )
-- 	-- tmr.create():alarm(5000, tmr.ALARM_SINGLE, function() dofile("init.lua") end )
-- 	print("...............at end of sleep function...")
-- end


-- print(tostring(wifi.getmode()).." "..wifi.NULLMODE)
-- if wifi.getmode() == wifi.NULLMODE then
-- 	print("done with sensors and wifi is off.  going to sleep")
-- 	go_to_sleep()
-- end