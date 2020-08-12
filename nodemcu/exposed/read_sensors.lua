history_file = "sensor_history_file"


sec, usec, rate = rtctime.get()
val = adc.read(0)



if file.exists(history_file) then
	decoder = sjson.decoder()
	decoder:write(file.getcontents(history_file))
	history = decoder:result()
else
	history = {}
end

history[sec] = val

file.putcontents(history_file, sjson.encode(history))