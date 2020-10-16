print("WIFI_ACTIONS: entering wifi_actions.lua")

-----------------------  SET HTTP REQUEST FILES TO PROCESS  -----------------------

local http_request_files = {
	"config_http_requests",
	"readings_http_requests"
}

-----------------------  LOG HANDLING  -----------------------


local function send_log()
	if logfile_to_send then
		local contents = logfile_to_send:read()
		if contents ~= nil then
			uart.write(0,"WIFI_ACTIONS: Sending a bit of the log\r\n")
			http.post(SERVER_URL.."/log",
				"mac: "..wifi.sta.getmac().."\r\ndevice-next-init: "..next_init_expected.."\r\nContent-Type: application/json\r\n",
				contents,
				send_log
				)
		else
			logfile_to_send:close()
			print("WIFI_ACTIONS: end of send_log, going to fetch_config")
		end
	end
end


if logfile then
	logfile:close()
	file.remove("logfile_to_send")
	local success = file.rename("logfile", "logfile_to_send")
	logfile = file.open("logfile", "w")
	logfile_to_send = file.open("logfile_to_send", "r")
	print("WIFI_ACTIONS: log copy success: "..tostring(success))
end


-----------------------  HTTP QUEUE CREATION  -----------------------


local http_queue = (require "fifo").new()

local function do_http_request(args)
	local type = args['type'] or "get"
	local url = args['url']
	local headers = args['headers'] or string.format("mac: %s\r\ndevice-next-init: %s\r\nContent-Type: application/json\r\n", wifi.sta.getmac(), rtcmem.read32(MEMSLOT_NEXT_INIT_EXPECTED))
	local body = args['body']
	local body_generator = args['body_generator']
	local callback = args['callback']
	local name = args['name']

	local function do_callback(...)
		if name then
			print("QUEUE: in do_callback for "..name)
		end

		if callback then
			callback(unpack(arg))
		end

		if not http_queue:dequeue(do_http_request) then
			print("QUEUE: done with queue, sending log")
			-- http_queue = nil
			-- send_log()
		end
	end

	if name then
		print("WIFI_ACTIONS: Performing request: "..name)
	end

	if type == "get" then
		http.get(url, headers, do_callback)
	elseif type == "post" then
		if body_generator then
			print("WIFI: body generator")
			http.post(url, headers, body_generator(), do_callback)
		else
			print("WIFI: plain body")
			http.post(url, headers, body, do_callback)
		end
	end
end


-----------------------  PROCESS FILES AND ENQUEUE REQUESTS  -----------------------


----- WE SHOULD ENQUEUE THE FILES AND PROCESS AND REQUEST THEM ONE AT A TIME.  EACH FILE CAN DO ONE REQUEST.



print("WIFI: processing requests")

for i, request_file in pairs(http_request_files) do
	print("WIFI_ACTIONS: Processing file "..request_file)
	for j, request_info in pairs(require(request_file)) do
		if request_info then
			http_queue:queue(request_info, do_http_request)
			print("WIFI: enqueuing request from "..request_file)
		else
			print("WIFI: no requests from "..request_file)
		end
	end
end


-----------------------  SNTP  -----------------------


sntp.sync("128.138.140.44", 
	function(seconds, microseconds, server, info)
		local sec, usec, rate = rtctime.get()
		-- rtcmem.write32(MEMSLOT_LAST_WIFI_TIME, sec)
		print("WIFI_ACTIONS: SNTP sync successful. Time: "..format_time(sec))
		if not http_queue:dequeue(do_http_request) then
			print("QUEUE: queue was empty")
		end
	end,
	function()
		local sec, usec, rate = rtctime.get()
		print("WIFI_ACTIONS: SNTP sync unsuccessful. Time: "..format_time(sec))
		if not http_queue:dequeue(do_http_request) then
			print("QUEUE: queue was empty")
		end
	end,
	nil)