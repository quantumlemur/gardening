-- RTC memory slots
-- Slots 21 - 31 are available

MEMSLOT_INITIALIZED = 21 -- Has the memory been initialized?
MEMSLOT_LAST_ENTRY_TIME = 22
MEMSLOT_LAST_INIT_TIME = 23
MEMSLOT_NEXT_INIT_TIME = 24 -- Next time to run INIT instead of ENTRY
MEMSLOT_MAX_ENTRYS_WITHOUT_INIT = 25 -- Max number of boots before falling back to INIT
MEMSLOT_ENTRYS_SINCE_INIT = 26
MEMSLOT_INIT_INTERVAL = 27 -- Max time between INITs
MEMSLOT_SLEEP_DURATION = 28
MEMSLOT_NEXT_INIT_EXPECTED = 29 -- calculated expectation of next init
MEMSLOT_LIGHT = 30


-- Config
DHT_PIN = 1
USE_RTCFIFO = false -- alternative is file-based logging


-- rtcmem.write32(MEMSLOT_INITIALIZED, 0)  -- reset memory next boot?


-- initialize the memory slots
if rtcmem.read32(MEMSLOT_INITIALIZED) ~= 1 then
	print("COMMON_DEFS: REINITIALIZING MEMORY")
	rtcmem.write32(MEMSLOT_INITIALIZED, 1)
	rtcmem.write32(MEMSLOT_LAST_ENTRY_TIME, 0)
	rtcmem.write32(MEMSLOT_LAST_INIT_TIME, 0)
	rtcmem.write32(MEMSLOT_NEXT_INIT_TIME, 0)
	rtcmem.write32(MEMSLOT_MAX_ENTRYS_WITHOUT_INIT, 10)
	rtcmem.write32(MEMSLOT_ENTRYS_SINCE_INIT, 0)
	rtcmem.write32(MEMSLOT_INIT_INTERVAL, 1)
	rtcmem.write32(MEMSLOT_SLEEP_DURATION, 3)
	rtcmem.write32(MEMSLOT_NEXT_INIT_EXPECTED, 0)
	rtcmem.write32(MEMSLOT_LIGHT, 1)
end


-- Format a UNIX timestamp into a local string
format_time = function(timestamp)
	local offset = - 7 * 60 * 60 -- seconds from UTC to local
	local newtime = timestamp + offset
	if newtime > 0 then
		local tm = rtctime.epoch2cal(timestamp + offset)
		return string.format("%04d/%02d/%02d %02d:%02d:%02d", tm["year"], tm["mon"], tm["day"], tm["hour"], tm["min"], tm["sec"])
	else
		return "0"
	end
end


-- Uncomment to enable file/network logging
-- logfile = file.open("logfile", "a")
-- print = function(string)
-- 	if logfile then
-- 		string = format_time(rtctime.get()).." "..string.."<br>"
-- 		logfile:write(string)
-- 	end
-- 	uart.write(0,string.."\r\n")
-- end

