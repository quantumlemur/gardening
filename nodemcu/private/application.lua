print("entering application.lua")


-- http.get("http://nuc:5000/status/application", "", "")

-- if file.exists("auth.lua") then
-- 	require("auth")
-- end

-- require("flash")

if file.exists("send_readings.lua") then
	require("send_readings")
end




