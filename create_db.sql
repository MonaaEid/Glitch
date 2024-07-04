-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS glitch;
CREATE USER IF NOT EXISTS 'gadmin'@'localhost' IDENTIFIED BY '';
GRANT ALL PRIVILEGES ON `glitch`.* TO 'gadmin'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'gadmin'@'localhost';
FLUSH PRIVILEGES;

