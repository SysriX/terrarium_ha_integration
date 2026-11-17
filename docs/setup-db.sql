-- Terrarium: create the database and user in MariaDB (run once as root,
-- e.g. phpMyAdmin -> SQL, or in the MariaDB container: mariadb -u root -p < setup-db.sql).
-- Replace <PASSWORD> with a password of your choice first.
--
-- Afterwards in Home Assistant: Settings -> Devices & services -> Terrarium -> Configure -> MariaDB database:
--   external server:  mysql://terrarium:<PASSWORD>@<HOST>/terrarium?charset=utf8mb4
--   MariaDB add-on:   mysql://terrarium:<PASSWORD>@core-mariadb/terrarium?charset=utf8mb4
-- The tables are created automatically on the first start; existing local data is copied into the database.

CREATE DATABASE IF NOT EXISTS terrarium CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'terrarium'@'%' IDENTIFIED BY '<PASSWORD>';
GRANT ALL PRIVILEGES ON terrarium.* TO 'terrarium'@'%';
FLUSH PRIVILEGES;
