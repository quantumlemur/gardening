DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS device_config;
DROP TABLE IF EXISTS device_status;
DROP TABLE IF EXISTS readings;


CREATE TABLE devices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mac TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  name TEXT
);


CREATE TABLE device_config (
  mac TEXT NOT NULL,
  wifi_connect_interval INTEGER NOT NULL,
  voltage_check_interval INTEGER NOT NULL,
  sleep_duration INTEGER NOT NULL,
  FOREIGN KEY(mac) REFERENCES devices(mac)
);


CREATE TABLE device_status (
  mac TEXT NOT NULL,
  last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  voltage INTEGER,
  log TEXT,
  FOREIGN KEY(mac) REFERENCES devices(mac)
);


CREATE TABLE readings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  mac TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  value INTEGER NOT NULL,
  offset INTEGER NOT NULL,
  name TEXT,
  FOREIGN KEY(mac) REFERENCES devices(mac)
);