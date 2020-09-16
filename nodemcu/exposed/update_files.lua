print("entering update_files.lua")


create_write_callback = function(filename, files_to_update)
	print("creating callback for "..filename)
	return function(status_code, body, headers)
		print("in callback for "..filename)
		if status_code == 200 then
			print("  updating "..filename)

			file.remove(string.gsub(filename, "\.lua", "\.lc"))

			if filename == "init.lua" then
				filename = "init.new"
			elseif filename == "update_files.lua" then
				filename = "update_files.new"
			end
			
			file.putcontents(filename, body)

			if file.exists("init.new") then
				file.flush()
				file.remove("init.old")
				file.rename("init.lua", "init.old")
				file.rename("init.new", "init.lua")
			end

			-- if file.exists(filename) then
			-- 	node.compile(filename)
			-- end

		end
		if files_to_update == nil then
			file.flush()
			-- print("file update complete.  Restarting...")
			-- tmr.create():alarm(1000, tmr.ALARM_SINGLE, function() node.restart() end )
		else
			local next_filename, next_files_to_update = table.remove(files_to_update)
			http.get("http://192.168.86.33:5000/api/getfile/"..next_filename, "", create_write_callback(next_filename, next_files_to_update))
		end
	end
end
	


file_is_changed = function(filename, hash)
	print("testing for file change on "..filename.." with hash "..hash)
	if file.exists(filename) then
		local device_hash = crypto.fhash("md5", filename)
		if encoder.toHex(device_hash) == hash then
			return false
		end
	end
	return true
end



check_for_updates = function(status_code, body, headers)
local files_to_update = {}
	if status_code == 200 then
		local decoder = sjson.decoder()
		decoder:write(body)
		local server_files = decoder:result()

		for key, file in pairs(server_files) do
			-- print(file[1])
			-- print(file[2])
			if file_is_changed(file[1], file[2]) then
				table.insert(files_to_update, file[1])
			end
		end
		if next(files_to_update) == nil then
			print("no files to update.  Continuing...")
			if file.exists("application.lua") then
				require("application")
			end
			go_to_sleep()
		else
			print("downloading new files...")
			local next_filename, next_files_to_update = table.remove(files_to_update)
			http.get("http://192.168.86.33:5000/api/getfile/"..next_filename, "", create_write_callback(next_filename, next_files_to_update))
		end
	end
end


http.get("http://192.168.86.33:5000/api/listfiles", "", check_for_updates)