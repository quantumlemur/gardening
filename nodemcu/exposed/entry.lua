
node.startupcommand("@init.lua")
print("***** Starting ENTRY.  Setting startupcomand to INIT")

-----------------------  SETUP  -----------------------

tmr.softwd(60) -- 60 second restart if something hangs


if package.loaded["COMMON_DEFS"] == nil then
	-- we're in here if INIT has not run
	require("COMMON_DEFS")
end

local sec, usec, rate = rtctime.get()
rtcmem.write32(MEMSLOT_LAST_ENTRY_TIME, sec)
rtcmem.write32(MEMSLOT_ENTRYS_SINCE_INIT, rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT) + 1)


-- write out status
print("ENTRY: last init time: "..format_time(rtcmem.read32(MEMSLOT_LAST_INIT_TIME)))
print("ENTRY: last entry time: "..format_time(rtcmem.read32(MEMSLOT_LAST_ENTRY_TIME)))
print("ENTRY: time now: "..format_time(rtctime.get()))
print("ENTRY: next init time: "..format_time(rtcmem.read32(MEMSLOT_NEXT_INIT_TIME)))

print("ENTRY: entry "..rtcmem.read32(MEMSLOT_ENTRYS_SINCE_INIT).." of "..rtcmem.read32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT).." before INIT")
print("ENTRY: max time between INITs: "..rtcmem.read32(MEMSLOT_INIT_INTERVAL))
print("ENTRY: sleep duration: "..rtcmem.read32(MEMSLOT_SLEEP_DURATION))




-- -- write out all user memory
-- for i=21,32 do
-- 	print("ENTRY: memslot "..i.." val: "..rtcmem.read32(i))
-- end

-----------------------  SENSORS  -----------------------


require("read_sensors")


-----------------------  WIFI  -----------------------


if wifi.sta.status() == wifi.STA_GOTIP then
	require("wifi_actions")
end

-----------------------  MOVE ON TO NEXT STEP  -----------------------

print("ENTRY: done with entry")
require("exit")
