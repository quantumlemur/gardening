DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS device_config;
DROP TABLE IF EXISTS device_status;
-- DROP TABLE IF EXISTS readings;


CREATE TABLE devices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mac TEXT NOT NULL,
  created INTEGER NOT NULL
);


CREATE TABLE device_config (
  device_id INTEGER NOT NULL,
  name TEXT,
  location_zone INTEGER NOT NULL DEFAULT 0,
  location_x INTEGER NOT NULL DEFAULT 0,
  location_y INTEGER NOT NULL DEFAULT 0,
  calibration_min INTEGER NOT NULL DEFAULT 0,
  calibration_max INTEGER NOT NULL DEFAULT 1000,
  trigger_min INTEGER NOT NULL DEFAULT 0,
  INIT_INTERVAL INTEGER NOT NULL DEFAULT 1,
  SLEEP_DURATION INTEGER NOT NULL DEFAULT 1,
  SLEEP_DELAY INTEGER NOT NULL DEFAULT 10,
  LIGHT INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(device_id) REFERENCES devices(id)
);


CREATE TABLE device_status (
  device_id INTEGER NOT NULL,
  checkin_time INTEGER,
  device_time INTEGER,
  device_next_init INTEGER,
  voltage INTEGER,
  log TEXT,
  FOREIGN KEY(device_id) REFERENCES devices(id)
);


-- CREATE TABLE readings (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   device_id INTEGER NOT NULL,
--   timestamp INTEGER NOT NULL,
--   value INTEGER NOT NULL,
--   offset INTEGER NOT NULL,
--   zscore FLOAT,
--   name TEXT,
--   FOREIGN KEY(device_id) REFERENCES devices(id)
-- );