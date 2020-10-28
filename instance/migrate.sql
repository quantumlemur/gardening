-- UPDATE readings SET timestamp = CAST(strftime('%s', timestamp) AS INTEGER);

-- UPDATE devices SET created = CAST(strftime('%s', created) AS INTEGER);

-- UPDATE device_status SET checkin_time = CAST(strftime('%s', checkin_time) AS INTEGER);

-- UPDATE device_status SET device_time = CAST(strftime('%s', device_time) AS INTEGER);

-- UPDATE device_status SET device_next_init = CAST(strftime('%s', device_next_init) AS INTEGER);


-- CREATE TABLE tempreadings (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   device_id INTEGER NOT NULL,
--   timestamp INTEGER NOT NULL,
--   value INTEGER NOT NULL,
--   offset INTEGER NOT NULL,
--   name TEXT,
--   FOREIGN KEY(device_id) REFERENCES devices(mac)
-- );

-- INSERT INTO tempreadings SELECT * FROM readings;

-- DROP TABLE IF EXISTS readings;

-- CREATE TABLE readings (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   device_id INTEGER NOT NULL,
--   timestamp INTEGER NOT NULL,
--   value INTEGER NOT NULL,
--   offset INTEGER NOT NULL,
--   name TEXT,
--   FOREIGN KEY(device_id) REFERENCES devices(mac)
-- );

-- INSERT INTO readings SELECT * FROM tempreadings;
-- DROP TABLE IF EXISTS tempreadings;









-- CREATE TABLE tempdevices (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   mac TEXT NOT NULL,
--   created INTEGER NOT NULL
-- );

-- INSERT INTO tempdevices SELECT * FROM devices;

-- DROP TABLE IF EXISTS devices;

-- CREATE TABLE devices (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   mac TEXT NOT NULL,
--   created INTEGER NOT NULL
-- );

-- INSERT INTO devices SELECT * FROM tempdevices;
-- DROP TABLE IF EXISTS tempdevices;





-- CREATE TABLE tempdevice_status (
--   device_id INTEGER NOT NULL,
--   checkin_time INTEGER,
--   device_time INTEGER,
--   device_next_init INTEGER,
--   voltage INTEGER,
--   log TEXT,
--   FOREIGN KEY(device_id) REFERENCES devices(id)
-- );

-- INSERT INTO tempdevice_status SELECT * FROM device_status;
-- DROP TABLE IF EXISTS device_status;

-- CREATE TABLE device_status (
--   device_id INTEGER NOT NULL,
--   checkin_time INTEGER,
--   device_time INTEGER,
--   device_next_init INTEGER,
--   voltage INTEGER,
--   log TEXT,
--   FOREIGN KEY(device_id) REFERENCES devices(id)
-- );

-- INSERT INTO device_status SELECT * FROM tempdevice_status;
-- DROP TABLE IF EXISTS tempdevice_status;


DROP TABLE IF EXISTS board_types;
DROP TABLE IF EXISTS device_config_temp;

CREATE TABLE board_types (
  board_type INTEGER PRIMARY KEY AUTOINCREMENT,
  board_name TEXT,
  PIN_SETTINGS TEXT NOT NULL DEFAULT "[]",
  SENSORS TEXT NOT NULL DEFAULT "[]",
  BOARD_LED_PIN INTEGER NOT NULL DEFAULT -1,
  BOARD_LED_PIN_INVERT INTEGER NOT NULL DEFAULT 0,
  R_LED_PIN INTEGER NOT NULL DEFAULT -1,
  G_LED_PIN INTEGER NOT NULL DEFAULT -1,
  B_LED_PIN INTEGER NOT NULL DEFAULT -1
);

INSERT INTO board_types (board_type, board_name, PIN_SETTINGS, SENSORS, BOARD_LED_PIN, BOARD_LED_PIN_INVERT, R_LED_PIN, G_LED_PIN, B_LED_PIN)
VALUES
(1, "Spike", "[]", '[{"sensorName": "soil", "pin": 32, "multiplier": 1}]', 16, 1, -1, -1, -1),
(2, "EzSBC Feather", '[{"pin":2, "mode":"OUT", "value":1, "pull":"NONE"},{"pin":15, "mode":"OUT", "value":1, "pull":"NONE"}]', '[{"sensorName": "volt", "pin": 35, "multiplier": 1.77289377289377}, {"sensorName": "soil", "pin": 33, "multiplier": 1}]', 13, 0, -1, -1, -1);


CREATE TABLE device_config_temp (
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
  board_type INTEGER NOT NULL DEFAULT 2,
  FOREIGN KEY(device_id) REFERENCES devices(id),
  FOREIGN KEY(board_type) REFERENCES board_types(board_type)
);

INSERT INTO device_config_temp 
SELECT
device_id,
name,
location_zone,
location_x,
location_y,
INIT_INTERVAL,
SLEEP_DURATION,
SLEEP_DELAY,
MAX_ENTRYS_WITHOUT_INIT,
LIGHT,
1
FROM device_config;

DROP TABLE IF EXISTS device_config;

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
  board_type INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY(device_id) REFERENCES devices(id),
  FOREIGN KEY(board_type) REFERENCES board_types(board_type)
);

INSERT INTO device_config
SELECT * FROM device_config_temp;

DROP TABLE IF EXISTS device_config_temp;

UPDATE device_config SET board_type=2 WHERE device_id=22;