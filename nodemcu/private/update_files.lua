

http.get("http://nuc:5000/status/updating_files", "", "")


create_write_callback = function(filename)
	return function(status_code, body, headers)
		if status_code == 200 then
			file.putcontents(filename, body)
			http.get("http://nuc:5000/status/restarting", "", "")
			tmr.create():alarm(5000, tmr.ALARM_SINGLE, function() node.restart() end)
		end
	end
end
	


check_for_file_change = function(filename, hash)
	if file.exists(filename) then
		device_hash = crypto.fhash("md5", filename)
		if encoder.toHex(device_hash) == hash then
			print("same")
		else
			http.get("http://nuc:5000/api/getfile/"..filename, "", create_write_callback(filename))
		end
	else
		http.get("http://nuc:5000/api/getfile/"..filename, "", create_write_callback(filename))
	end
end


check_for_updates = function(status_code, body, headers)
	if status_code == 200 then
		decoder = sjson.decoder()
		decoder:write(body)
		server_files = decoder:result()

		for key, file in pairs(server_files) do
			check_for_file_change(file[1], file[2])
		end
	end
end


http.get("http://nuc:5000/api/listfiles", "", check_for_updates)