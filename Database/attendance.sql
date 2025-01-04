-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 26, 2024 at 05:53 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `attendance`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendancedata`
--

CREATE TABLE `attendancedata` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `enrollment` varchar(15) NOT NULL,
  `classroom` varchar(30) NOT NULL,
  `subject` varchar(20) NOT NULL,
  `date` date NOT NULL,
  `time` time NOT NULL,
  `code` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `studentsdata`
--

CREATE TABLE `studentsdata` (
  `id` int(11) NOT NULL,
  `name` text NOT NULL,
  `enrollment` varchar(20) NOT NULL,
  `contact` varchar(15) NOT NULL,
  `code` varchar(40) NOT NULL,
  `email` varchar(50) NOT NULL,
  `classroom` varchar(30) NOT NULL,
  `image` longblob NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendancedata`
--
ALTER TABLE `attendancedata`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `studentsdata`
--
ALTER TABLE `studentsdata`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendancedata`
--
ALTER TABLE `attendancedata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `studentsdata`
--
ALTER TABLE `studentsdata`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
