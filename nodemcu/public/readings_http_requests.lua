



local function handle_submission(status_code, body, headers)
    body_generator = nil
	if status_code == 200 then
		print("READINGS: readings sent successfully")
		file.remove("sensorfile")
	else
		print("READINGS: reading send failed")
	end
end



local function body_generator()
    local history_json = ""

    if USE_RTCFIFO then
        if rtcfifo.peek() then
            print("READINGS: reading rtcfifo")
            local timestamp, value, neg_e, name = rtcfifo.pop()
            history_json = history_json..string.format("[%d, %d, %d, \"%s\"]", timestamp, value, neg_e, name)
        end
        while rtcfifo.peek() do
            local timestamp, value, neg_e, name = rtcfifo.pop()
            history_json = history_json..string.format(",\r\n[%d, %d, %d, \"%s\"]", timestamp, value, neg_e, name)
        end
    else
        local sensorFile = file.open("sensorfile", "r")
        if sensorFile then

            local fileChunk = sensorFile:read()
            while fileChunk do
                history_json = history_json..fileChunk
                fileChunk = sensorFile:read()
            end

            sensorFile:close(); sensorFile=nil
        end
    end
    local output = "[\r\n"..history_json.."\r\n]"
    print(output)
    return output
end



return {
    {
        name = "sending readings",
        type = "post",
        url = SERVER_URL.."/readings",
        body_generator = body_generator,
        callback = handle_submission
    }
}


-- if string.len(history_json) > 0 then
--     print("READINGS: sending history")

--     history_json = "[\r\n"..history_json.."\r\n]"
--     print(history_json)

--     return {
--         {
--             name = "sending readings",
--             type = "post",
--             url = SERVER_URL.."/readings",
--             body_generator = body_generator,
--             callback = handle_submission
--         }
--     }
-- else
--     print("WIFI_ACTIONS: no history to send")
--     return {}
-- end
