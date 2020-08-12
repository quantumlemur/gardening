wifi_in_use = true

-- sec, usec, rate = rtctime.get()
-- file.putcontents("next_wifi_time", sec + wifi_interval)
-- http.get("http://nuc:5000/status/wifi_connected", "", "")
-- http.get("http://nuc:5000/status/current_time1="..tostring(sec), "", "")
-- sntp.sync("129.6.15.28", callback, errorcallback, nil)
-- sec, usec, rate = rtctime.get()
-- http.get("http://nuc:5000/status/current_time2="..tostring(sec), "", "")

-- load credentials, 'SSID' and 'PASSWORD' declared and initialize in there
dofile("credentials.lua")

callback = function(seconds, microseconds, server, info)
  http.get("http://nuc:5000/status/sntp_success", "", "")
  -- http.get("http://nuc:5000/status/sntp_offset="..tostring(sntp.getoffset()), "", "")
  sec, usec, rate = rtctime.get()
  http.get("http://nuc:5000/status/post_sync_time="..tostring(sec), "", "")
end

errorcallback = function(type, info)
  http.get("http://nuc:5000/status/sntp_failure", "", "")
end

function startup()
    if file.open("init.lua") == nil then
        print("init.lua deleted or renamed")
    else
        print("Running")
        file.close("init.lua")
        sec, usec, rate = rtctime.get()
        file.putcontents("next_wifi_time", sec + wifi_interval)
        http.get("http://nuc:5000/status/wifi_connected", "", "")
        http.get("http://nuc:5000/status/pre_sync_time="..tostring(sec), "", "")
        -- sntp.sync({"129.6.15.28", "132.163.97.1", "132.163.96.1", "128.138.140.44"}, callback, errorcallback, nil)
        sntp.sync("129.6.15.28", callback, errorcallback, nil)
        dofile("update_files.lua")
        tmr.create():alarm(10000, tmr.ALARM_SINGLE, function() dofile("application.lua") end)
    end
end

-- Define WiFi station event callbacks
wifi_connect_event = function(T)
  print("Connection to AP("..T.SSID..") established!")
  print("Waiting for IP address...")
  if disconnect_ct ~= nil then disconnect_ct = nil end
end

wifi_got_ip_event = function(T)
  -- Note: Having an IP address does not mean there is internet access!
  -- Internet connectivity can be determined with net.dns.resolve().
  print("Wifi connection is ready! IP address is: "..T.IP)
  print("Startup will resume momentarily, you have 3 seconds to abort.")
  print("Waiting...")
  tmr.create():alarm(3000, tmr.ALARM_SINGLE, startup)
end

wifi_disconnect_event = function(T)
  if T.reason == wifi.eventmon.reason.ASSOC_LEAVE then
    --the station has disassociated from a previously connected AP
    return
  end
  -- total_tries: how many times the station will attempt to connect to the AP. Should consider AP reboot duration.
  local total_tries = 75
  print("\nWiFi connection to AP("..T.SSID..") has failed!")

  --There are many possible disconnect reasons, the following iterates through
  --the list and returns the string corresponding to the disconnect reason.
  for key,val in pairs(wifi.eventmon.reason) do
    if val == T.reason then
      print("Disconnect reason: "..val.."("..key..")")
      break
    end
  end

  if disconnect_ct == nil then
    disconnect_ct = 1
  else
    disconnect_ct = disconnect_ct + 1
  end
  if disconnect_ct < total_tries then
    print("Retrying connection...(attempt "..(disconnect_ct+1).." of "..total_tries..")")
  else
    wifi.sta.disconnect()
    print("Aborting connection to AP!")
    disconnect_ct = nil
  end
end

-- Register WiFi Station event callbacks
wifi.eventmon.register(wifi.eventmon.STA_CONNECTED, wifi_connect_event)
wifi.eventmon.register(wifi.eventmon.STA_GOT_IP, wifi_got_ip_event)
wifi.eventmon.register(wifi.eventmon.STA_DISCONNECTED, wifi_disconnect_event)

print("Connecting to WiFi access point...")
wifi.setmode(wifi.STATION)
wifi.sta.config({ssid=SSID, pwd=PASSWORD})
-- wifi.sta.connect() not necessary because config() uses auto-connect=true by default