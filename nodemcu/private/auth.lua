
identity_file = "identity"
session_file = "session"


handle_registration = function(status_code, body, headers)
	if status_code == 200 then
		http.get("http://nuc:5000/status/register_success", "", "")
	else
		file.remove(identity_file)
		http.get("http://nuc:5000/status/register_fail", "", "")
		http.get("http://nuc:5000/status/restarting", "", "")
		tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() node.restart() end)
	end
end


if file.exists(identity_file) then
	-- decoder = sjson.decoder()
	-- decoder:write(file.getcontents(identity_file))
	identity = file.getcontents(identity_file)
else
	username = node.chipid()
	password = tostring(node.chipid())..tostring(rtctime.get())..tostring(node.random(1000000000))
	password = encoder.toHex(crypto.hash("sha1", password))
	identity = "username="..username.."&password="..password
	--identity["username"] = username
	--identity["password"] = password
	--encoder = sjson.encoder(identity)
	file.putcontents(identity_file, identity)
	http.post("http://nuc:5000/auth/register",
		"Content-Type: application/x-www-form-urlencoded\r\n", identity, handle_registration)
end





