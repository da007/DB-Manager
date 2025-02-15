CREATE DATABASE  IF NOT EXISTS `repair_shop` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `repair_shop`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: repair_shop
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clients` (
  `ClientID` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(255) NOT NULL,
  `LastName` varchar(255) NOT NULL,
  `PhoneNumber` varchar(20) NOT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `Address` text,
  `Notes` text,
  PRIMARY KEY (`ClientID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clients`
--

LOCK TABLES `clients` WRITE;
/*!40000 ALTER TABLE `clients` DISABLE KEYS */;
INSERT INTO `clients` VALUES (1,'Алексей','Смирнов','+79211112233','smirnov.a@mail.ru','ул. Пушкина, д. 10, кв. 5','Почти постоянный клиент'),(2,'Мария','Иванова','+79212223344','ivanova.m@gmail.com','пр. Ленина, д. 25, кв. 12',NULL),(3,'Игорь','Петров','+79213334455','petrov.i@yandex.ru','ул. Гагарина, д. 5, кв. 3','Срочный ремонт'),(4,'Екатерина','Сидорова','+79214445566','sidorova.e@mail.ru','ул. Советская, д. 18, кв. 8',NULL),(5,'Андрей','Козлов','+79215556677','kozlov.a@gmail.com','пр. Мира, д. 30, кв. 15','Скидка по карте'),(6,'Наталья','Морозова','+79216667788','morozova.n@yandex.ru','ул. Центральная, д. 7, кв. 2',NULL),(7,'Сергей','Волков','+79217778899','volkov.s@mail.ru','ул. Лесная, д. 12, кв. 6','Забрать в пятницу'),(8,'Юлия','Лебедева','+79218889900','lebedeva.y@gmail.com','пр. Победы, д. 42, кв. 20',NULL),(9,'Павел','Соколов','+79219990011','sokolov.p@yandex.ru','ул. Садовая, д. 9, кв. 4',NULL),(10,'Ольга','Орлова','+79210001122','orlova.o@mail.ru','ул. Новая, д. 1, кв. 1','Не звонить после 20:00'),(13,'Тимур ','Насыров ','+77713088676','','большой дом','человек ');
/*!40000 ALTER TABLE `clients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devices` (
  `DeviceID` int NOT NULL AUTO_INCREMENT,
  `DeviceTypeID` int NOT NULL,
  `Brand` varchar(255) NOT NULL,
  `Model` varchar(255) NOT NULL,
  `SerialNumber` varchar(255) DEFAULT NULL,
  `Description` text,
  PRIMARY KEY (`DeviceID`),
  UNIQUE KEY `SerialNumber` (`SerialNumber`),
  KEY `DeviceTypeID` (`DeviceTypeID`),
  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`DeviceTypeID`) REFERENCES `devicetypes` (`DeviceTypeID`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES (1,1,'Asus','X540','SN123456','Не включается'),(2,1,'HP','Pavilion 15','SN789012','Разбит экран'),(3,1,'Lenovo','IdeaPad 3','SN345678','Проблемы с клавиатурой'),(4,1,'Acer','Aspire 5','SN901234',NULL),(5,2,'Dell','OptiPlex 3080','SN567890','Зависает при загрузке'),(6,2,'HP','EliteDesk 800','SN234567',NULL),(7,3,'HP','LaserJet Pro M404dn','SN890123','Не печатает'),(8,3,'Canon','imageCLASS MF237w','SN456789','Замятие бумаги'),(9,3,'Epson','L3250','SN654327',NULL),(10,4,'Canon','CanoScan LiDE 300','SN012345','Не определяется компьютером'),(11,5,'Dell','U2422H','SN678901','Полосы на экране'),(12,5,'Samsung','C27F390','SN654387',NULL);
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devicetypes`
--

DROP TABLE IF EXISTS `devicetypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devicetypes` (
  `DeviceTypeID` int NOT NULL AUTO_INCREMENT,
  `TypeName` varchar(255) NOT NULL,
  PRIMARY KEY (`DeviceTypeID`),
  UNIQUE KEY `TypeName` (`TypeName`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devicetypes`
--

LOCK TABLES `devicetypes` WRITE;
/*!40000 ALTER TABLE `devicetypes` DISABLE KEYS */;
INSERT INTO `devicetypes` VALUES (5,'Монитор'),(1,'Ноутбук'),(2,'ПК'),(3,'Принтер'),(4,'Сканер');
/*!40000 ALTER TABLE `devicetypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `EmployeeID` int NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(255) NOT NULL,
  `LastName` varchar(255) NOT NULL,
  `Position` varchar(255) NOT NULL,
  `PhoneNumber` varchar(20) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `HireDate` date DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`EmployeeID`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,'Иван','Иванов','Старший мастер','+79111234567','ivanov@remont.local','2022-01-15',1),(2,'Петр','Петров','Мастер','+79112345678','petrov@remont.local','2022-03-10',1),(3,'Сергей','Сидоров','Мастер','+79113456789','sidorov@remont.local','2022-05-20',1),(4,'Анна','Кузнецова','Менеджер','+79114567890','kuznetsova@remont.local','2023-01-10',1),(5,'Елена','Смирнова','Приемщик заказов','+79115678901','smirnova@remont.local','2023-03-01',1),(6,'Дмитрий','Михайлов','Мастер','+79116789012','mikhailov@remont.local','2023-06-15',1),(7,'Ольга','Васильева','Стажер','+79117890123','vasilyeva@remont.local','2024-01-10',1),(8,'шах','челнок ','майор','8800555355','durka@gmail.com','1947-06-16',1);
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `OrderID` int NOT NULL AUTO_INCREMENT,
  `ClientID` int NOT NULL,
  `DeviceID` int NOT NULL,
  `EmployeeID` int DEFAULT NULL,
  `AssignedEmployeeID` int DEFAULT NULL,
  `StatusID` int NOT NULL DEFAULT '1',
  `DateCreated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `DateCompleted` datetime DEFAULT NULL,
  `ProblemDescription` text NOT NULL,
  `Diagnosis` text,
  `TotalPrice` decimal(10,2) DEFAULT NULL,
  `Notes` text,
  PRIMARY KEY (`OrderID`),
  KEY `ClientID` (`ClientID`),
  KEY `DeviceID` (`DeviceID`),
  KEY `EmployeeID` (`EmployeeID`),
  KEY `AssignedEmployeeID` (`AssignedEmployeeID`),
  KEY `StatusID` (`StatusID`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`ClientID`) REFERENCES `clients` (`ClientID`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`DeviceID`) REFERENCES `devices` (`DeviceID`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`EmployeeID`) REFERENCES `employees` (`EmployeeID`),
  CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`AssignedEmployeeID`) REFERENCES `employees` (`EmployeeID`),
  CONSTRAINT `orders_ibfk_5` FOREIGN KEY (`StatusID`) REFERENCES `statuses` (`StatusID`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,1,1,5,2,2,'2024-05-15 09:30:00',NULL,'Ноутбук Asus X540 не включается','Проблема с цепью питания',NULL,'Клиент Смирнов А.'),(2,2,2,5,1,3,'2024-05-15 10:15:00',NULL,'Разбит экран ноутбука HP Pavilion 15','Требуется замена матрицы',NULL,'Срочный ремонт'),(3,3,3,5,3,1,'2024-05-15 11:00:00',NULL,'Проблемы с клавиатурой Lenovo IdeaPad 3',NULL,NULL,NULL),(4,4,4,5,2,4,'2024-05-16 14:20:00',NULL,'Ноутбук Acer Aspire 5 - нужна чистка','Сильное загрязнение, требуется чистка и замена термопасты',NULL,NULL),(5,5,5,4,1,2,'2024-05-16 16:45:00',NULL,'ПК Dell OptiPlex 3080 зависает при загрузке','Проблема с жестким диском или ОС',NULL,NULL),(6,6,6,4,3,1,'2024-05-17 10:00:00',NULL,'ПК HP EliteDesk 800 - не включается',NULL,NULL,NULL),(7,7,7,4,2,5,'2024-05-17 12:30:00',NULL,'Принтер HP LaserJet Pro M404dn не печатает','Закончился тонер',NULL,'Заменить картридж'),(8,8,8,4,1,6,'2024-05-18 11:10:00',NULL,'Замятие бумаги в Canon imageCLASS MF237w','Замятие в лотке подачи',NULL,NULL),(9,9,9,4,1,7,'2024-05-19 14:00:00',NULL,'Принтер Epson L3250 выдает ошибку',NULL,NULL,'Выдан клиенту'),(10,10,10,5,3,2,'2024-05-19 17:25:00',NULL,'Сканер Canon CanoScan LiDE 300 не определяется','Проблема с драйверами или USB',NULL,NULL),(11,1,11,4,2,3,'2024-05-20 09:50:00',NULL,'Монитор Dell U2422H - полосы на экране','Повреждена матрица',NULL,'Клиент Смирнов (второй заказ)'),(12,3,12,5,1,1,'2024-05-20 13:15:00',NULL,'Монитор Samsung C27F390 не включается',NULL,NULL,NULL);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderservices`
--

DROP TABLE IF EXISTS `orderservices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderservices` (
  `OrderID` int NOT NULL,
  `ServiceID` int NOT NULL,
  `Price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`OrderID`,`ServiceID`),
  KEY `ServiceID` (`ServiceID`),
  CONSTRAINT `orderservices_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`),
  CONSTRAINT `orderservices_ibfk_2` FOREIGN KEY (`ServiceID`) REFERENCES `services` (`ServiceID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderservices`
--

LOCK TABLES `orderservices` WRITE;
/*!40000 ALTER TABLE `orderservices` DISABLE KEYS */;
INSERT INTO `orderservices` VALUES (1,1,500.00),(1,5,1200.00),(2,1,500.00),(2,2,4000.00),(3,1,500.00),(4,1,500.00),(4,4,1000.00),(5,1,500.00),(5,3,1500.00),(6,1,500.00),(7,1,500.00),(8,1,500.00),(9,1,500.00),(10,1,500.00),(11,1,500.00),(11,2,4000.00),(12,1,500.00);
/*!40000 ALTER TABLE `orderservices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orderspareparts`
--

DROP TABLE IF EXISTS `orderspareparts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orderspareparts` (
  `OrderID` int NOT NULL,
  `SparePartID` int NOT NULL,
  `QuantityUsed` int NOT NULL,
  `PricePerUnit` decimal(10,2) NOT NULL,
  PRIMARY KEY (`OrderID`,`SparePartID`),
  KEY `SparePartID` (`SparePartID`),
  CONSTRAINT `orderspareparts_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `orders` (`OrderID`),
  CONSTRAINT `orderspareparts_ibfk_2` FOREIGN KEY (`SparePartID`) REFERENCES `spareparts` (`SparePartID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orderspareparts`
--

LOCK TABLES `orderspareparts` WRITE;
/*!40000 ALTER TABLE `orderspareparts` DISABLE KEYS */;
INSERT INTO `orderspareparts` VALUES (1,13,1,1000.00),(2,1,1,25000.00),(4,10,1,800.00),(5,5,1,18000.00),(7,11,1,25000.00),(8,12,1,19000.00),(11,1,1,25000.00);
/*!40000 ALTER TABLE `orderspareparts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` enum('Administrator','Operator','Master','Storage') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrator'),(2,'Operator'),(3,'Master'),(4,'Storage');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `services`
--

DROP TABLE IF EXISTS `services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `services` (
  `ServiceID` int NOT NULL AUTO_INCREMENT,
  `ServiceName` varchar(255) NOT NULL,
  `Description` text,
  `Price` decimal(10,2) NOT NULL,
  `IsHardware` tinyint(1) NOT NULL,
  PRIMARY KEY (`ServiceID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `services`
--

LOCK TABLES `services` WRITE;
/*!40000 ALTER TABLE `services` DISABLE KEYS */;
INSERT INTO `services` VALUES (1,'Диагностика','Полная диагностика устройства',500.00,0),(2,'Замена матрицы ноутбука','Замена поврежденной матрицы на новую',4000.00,1),(3,'Установка Windows','Установка операционной системы Windows',1500.00,0),(4,'Чистка системы охлаждения','Чистка от пыли и замена термопасты',1000.00,1),(5,'Замена разъема питания','Перепайка разъема питания',1200.00,1),(6,'Восстановление данных','Восстановление удаленных данных',3000.00,0);
/*!40000 ALTER TABLE `services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `spareparts`
--

DROP TABLE IF EXISTS `spareparts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spareparts` (
  `SparePartID` int NOT NULL AUTO_INCREMENT,
  `PartName` varchar(255) NOT NULL,
  `Description` text,
  `Manufacturer` varchar(255) DEFAULT NULL,
  `PartNumber` varchar(255) DEFAULT NULL,
  `QuantityInStock` int NOT NULL DEFAULT '0',
  `PurchasePrice` decimal(10,2) DEFAULT NULL,
  `SellingPrice` decimal(10,2) NOT NULL,
  `CompatibleDevices` text,
  PRIMARY KEY (`SparePartID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spareparts`
--

LOCK TABLES `spareparts` WRITE;
/*!40000 ALTER TABLE `spareparts` DISABLE KEYS */;
INSERT INTO `spareparts` VALUES (1,'Матрица для ноутбука 15.6\"','Матрица 1920x1080, LED, Slim','AU Optronics','B156HTN03.8',10,15000.00,25000.00,'Asus X540, Lenovo IdeaPad 3, Acer Aspire 5'),(2,'Матрица для ноутбука 17.3\"','Матрица 1600x900, LED','LG Display','LP173WD1',5,18000.00,30000.00,'HP Pavilion 17, Dell Inspiron 17'),(3,'Клавиатура для ноутбука Asus X540','Клавиатура, русская раскладка','Asus','KBD-X540',20,5000.00,8000.00,'Asus X540'),(4,'Клавиатура для ноутбука Lenovo IdeaPad 3','Клавиатура, рус/англ раскладка','Lenovo','KBD-IP3',15,6000.00,9500.00,'Lenovo IdeaPad 3'),(5,'SSD 256GB','Твердотельный накопитель, 2.5\", SATA III','Samsung','870 EVO 256GB',30,12000.00,18000.00,'Любые ноутбуки и ПК с SATA'),(6,'SSD 512GB','Твердотельный накопитель, M.2 NVMe PCIe','Kingston','KC3000 512GB',25,20000.00,30000.00,'Любые ноутбуки и ПК с M.2 NVMe'),(7,'Оперативная память DDR4 8GB','Модуль памяти, 2666MHz','Crucial','CT8G4SFS8266',40,7000.00,11000.00,'Любые ноутбуки с DDR4'),(8,'Оперативная память DDR5 16GB','Модуль памяти, 4800MHz','Corsair','CMK16GX5M1A4800C40',10,35000.00,50000.00,'Современные ПК с DDR5'),(9,'Блок питания для ПК 500W','Блок питания, ATX','Chieftec','CTG-500-80P',12,8000.00,12000.00,'Любые ПК'),(10,'Термопаста','Термопаста, 3 грамма','Arctic','MX-4',50,500.00,800.00,NULL),(11,'Картридж для принтера HP LaserJet Pro M404dn','Черный картридж, оригинальный','HP','CF259A',8,18000.00,25000.00,'HP LaserJet Pro M404dn'),(12,'Фотобарабан для принтера Canon imageCLASS MF237w','Фотобарабан','Canon','Drum 051',3,12000.00,19000.00,'Canon imageCLASS MF237w'),(13,'Разъем питания для ноутбука','5.5x2.5mm','NoName','DC-Jack-5525',100,300.00,1000.00,'Многие модели ноутбуков');
/*!40000 ALTER TABLE `spareparts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statuses`
--

DROP TABLE IF EXISTS `statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statuses` (
  `StatusID` int NOT NULL AUTO_INCREMENT,
  `StatusName` varchar(50) NOT NULL,
  PRIMARY KEY (`StatusID`),
  UNIQUE KEY `StatusName` (`StatusName`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statuses`
--

LOCK TABLES `statuses` WRITE;
/*!40000 ALTER TABLE `statuses` DISABLE KEYS */;
INSERT INTO `statuses` VALUES (2,'В диагностике'),(4,'В ремонте'),(6,'Выдан'),(5,'Готов'),(3,'Ожидает запчасти'),(7,'Отменен'),(1,'Принят');
/*!40000 ALTER TABLE `statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `login` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login` (`login`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'danhack007','$2b$12$6AxBPFetY5I6Ijvm5lB3x.8jdb.qpNcY2QBfjoFyW4ixFGjmfXUGm',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-02-16  2:44:58
