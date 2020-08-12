history_file = "sensor_history_file"

history = file.getcontents(history_file))

handle_submission = function(status_code, body, headers)
	if status_code == 200 then
		file.remove(history_file)
	end
end

http.post("http://nuc:5000/api/readings/"..history,
	"", history, handle_registration)