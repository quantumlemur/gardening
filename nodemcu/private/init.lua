sec, usec, rate = rtctime.get()
print(tostring(sec))
wifi_in_use = false
gpio.write(0, 0)


-- ensure DAC is set to read external voltage
if adc.force_init_mode(adc.INIT_ADC)
then
  node.restart()
  return -- don't bother continuing, the restart is scheduled
end


-- create timer files if they don't exist
if not file.exists("last_boot_time") then
  file.putcontents("last_boot_time", 0)
end

if not file.exists("next_wifi_time") then
  file.putcontents("next_wifi_time", 0)
end

if not file.exists("wifi_interval") then
  file.putcontents("wifi_interval", 60) -- seconds
end

if not file.exists("sleep_interval") then
  file.putcontents("sleep_interval", 10) -- seconds
end

-- read timer files
last_boot_time = tonumber(file.getcontents("last_boot_time"))
next_wifi_time = tonumber(file.getcontents("next_wifi_time"))
wifi_interval = tonumber(file.getcontents("wifi_interval"))
sleep_interval = tonumber(file.getcontents("sleep_interval"))


-- store the current boot time
file.putcontents("last_boot_time", tostring(sec))

-- if it's past time to connect to wifi, 
-- or I've restarted twice within the past 5 seconds, 
-- then connect to wifi
if (sec > next_wifi_time) or (sec - last_boot_time < 5) then
  wifi_in_use = true
  dofile("connect_wifi.lua")
end

-- read from the sensors
dofile("no_wifi.lua")


if wifi_in_use then
  tmr.create():alarm(60000, tmr.ALARM_SINGLE, function() rtctime.dsleep(sleep_interval*1000000) end)
else
  rtctime.dsleep(sleep_interval*1000000)
end

