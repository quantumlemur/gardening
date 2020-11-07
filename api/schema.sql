-- DROP TABLE IF EXISTS devices;
-- DROP TABLE IF EXISTS device_config;
-- DROP TABLE IF EXISTS device_status;
-- DROP TABLE IF EXISTS readings;


CREATE TABLE devices (
  id INTEGER PRIMARY KEY AUTOINCREMENT, -- change to device_id
  mac TEXT NOT NULL,
  created INTEGER NOT NULL
);


CREATE TABLE device_config (
  device_id INTEGER NOT NULL,
  name TEXT,
  location_zone INTEGER NOT NULL DEFAULT 0,
  location_x INTEGER NOT NULL DEFAULT 0,
  location_y INTEGER NOT NULL DEFAULT 0,
  INIT_INTERVAL INTEGER NOT NULL DEFAULT 1,
  SLEEP_DURATION INTEGER NOT NULL DEFAULT 1,
  SLEEP_DELAY INTEGER NOT NULL DEFAULT 10,
  MAX_ENTRYS_WITHOUT_INIT INTEGER NOT NULL DEFAULT 3,
  LIGHT INTEGER NOT NULL DEFAULT 1,
  board_id INTEGER NOT NULL DEFAULT 1,
  requested_version_tag TEXT DEFAULT "",
  FOREIGN KEY(device_id) REFERENCES devices(id),
  FOREIGN KEY(board_id) REFERENCES board_types(board_id)
);


CREATE TABLE device_status (
  device_id INTEGER NOT NULL,
  checkin_time INTEGER,
  device_time INTEGER,
  device_next_init INTEGER,
  voltage INTEGER, -- not used
  log TEXT, -- not used
  update_status TEXT,
  last_update_time INTEGER,
  current_version_hash TEXT,
  current_version_tag TEXT,
  last_update_attempt_time INTEGER,
  last_update_attempt_version TEXT,
  FOREIGN KEY(device_id) REFERENCES devices(id)
);


-- CREATE TABLE readings (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   device_id INTEGER NOT NULL,
--   timestamp INTEGER NOT NULL,
--   value INTEGER NOT NULL,
--   offset INTEGER NOT NULL,
--   zscore FLOAT,
--   name TEXT, -- change to sensorName
--   FOREIGN KEY(device_id) REFERENCES devices(id)
-- );


CREATE TABLE board_types (
  board_id INTEGER PRIMARY KEY AUTOINCREMENT,
  board_name TEXT,
  HIGH_PINS TEXT NOT NULL DEFAULT "[]",
  LOW_PINS TEXT NOT NULL DEFAULT "[]",
  SENSORS TEXT NOT NULL DEFAULT "[]",
  BOARD_LED_PIN INTEGER NOT NULL DEFAULT -1,
  BOARD_LED_PIN_INVERT INTEGER NOT NULL DEFAULT 0,
  R_LED_PIN INTEGER NOT NULL DEFAULT -1,
  G_LED_PIN INTEGER NOT NULL DEFAULT -1,
  B_LED_PIN INTEGER NOT NULL DEFAULT -1
);


CREATE TABLE zones (
    zone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_name TEXT,
    file_name TEXT NOT NULL,
    image_width INTEGER NOT NULL,
    image_height INTEGER NOT NULL
);