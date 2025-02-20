CREATE DATABASE  IF NOT EXISTS `repair_shop`
USE `repair_shop`;

CREATE TABLE `clients` (
  `client_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `phone_number` varchar(20) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `address` text,
  `notes` text,
  PRIMARY KEY (`client_id`)
)

CREATE TABLE `device_types` (
  `device_type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(255) NOT NULL,
  PRIMARY KEY (`device_type_id`),
  UNIQUE KEY `type_name` (`type_name`)
)

CREATE TABLE `devices` (
  `device_id` int NOT NULL AUTO_INCREMENT,
  `device_type_id` int NOT NULL,
  `brand` varchar(255) NOT NULL,
  `model` varchar(255) NOT NULL,
  `serial_number` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`device_id`),
  UNIQUE KEY `serial_number` (`serial_number`),
  KEY `device_type_id` (`device_type_id`),
  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`device_type_id`) REFERENCES `device_types` (`device_type_id`)
)

CREATE TABLE `employees` (
  `employee_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `position` varchar(255) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`employee_id`)
)

CREATE TABLE `order_services` (
  `order_id` int NOT NULL,
  `service_id` int NOT NULL,
  `price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`order_id`,`service_id`),
  KEY `service_id` (`service_id`),
  CONSTRAINT `order_services_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `order_services_ibfk_2` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`)
)

CREATE TABLE `order_spare_parts` (
  `order_id` int NOT NULL,
  `spare_part_id` int NOT NULL,
  `quantity_used` int NOT NULL,
  `price_per_unit` decimal(10,2) NOT NULL,
  PRIMARY KEY (`order_id`,`spare_part_id`),
  KEY `spare_part_id` (`spare_part_id`),
  CONSTRAINT `order_spare_parts_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`),
  CONSTRAINT `order_spare_parts_ibfk_2` FOREIGN KEY (`spare_part_id`) REFERENCES `spare_parts` (`spare_part_id`)
)

CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `client_id` int NOT NULL,
  `device_id` int NOT NULL,
  `employee_id` int DEFAULT NULL,
  `assigned_employee_id` int DEFAULT NULL,
  `status_id` int NOT NULL DEFAULT '1',
  `date_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `date_completed` datetime DEFAULT NULL,
  `problem_description` text NOT NULL,
  `diagnosis` text,
  `total_price` decimal(10,2) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`order_id`),
  KEY `client_id` (`client_id`),
  KEY `device_id` (`device_id`),
  KEY `employee_id` (`employee_id`),
  KEY `assigned_employee_id` (`assigned_employee_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`client_id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`),
  CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`assigned_employee_id`) REFERENCES `employees` (`employee_id`),
  CONSTRAINT `orders_ibfk_5` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`status_id`)
)

CREATE TABLE `roles` (
  `role_id` int NOT NULL AUTO_INCREMENT,
  `role_name` enum('Administrator','Operator','Master','Storage') NOT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
)

CREATE TABLE `services` (
  `service_id` int NOT NULL AUTO_INCREMENT,
  `service_name` varchar(255) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `is_hardware` tinyint(1) NOT NULL,
  PRIMARY KEY (`service_id`)
)

CREATE TABLE `spare_parts` (
  `spare_part_id` int NOT NULL AUTO_INCREMENT,
  `part_name` varchar(255) NOT NULL,
  `description` text,
  `manufacturer` varchar(255) DEFAULT NULL,
  `part_number` varchar(255) DEFAULT NULL,
  `quantity_in_stock` int NOT NULL DEFAULT '0',
  `purchase_price` decimal(10,2) DEFAULT NULL,
  `selling_price` decimal(10,2) NOT NULL,
  `compatible_devices` text,
  PRIMARY KEY (`spare_part_id`)
)

CREATE TABLE `statuses` (
  `status_id` int NOT NULL AUTO_INCREMENT,
  `status_name` varchar(50) NOT NULL,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_name` (`status_name`)
)

CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `login` (`login`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE RESTRICT ON UPDATE CASCADE
)