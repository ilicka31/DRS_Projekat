-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 26, 2023 at 07:09 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.1.12


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `drs_baza`
--

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `hashID` varchar(255) NOT NULL,
  `sender` varchar(30) NOT NULL,
  `receiver` varchar(30) NOT NULL,
  `time` datetime NOT NULL,
  `amount` double NOT NULL,
  `currency` varchar(10) NOT NULL,
  `status` varchar(15) NOT NULL
);

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`hashID`, `sender`, `receiver`, `time`, `amount`, `currency`, `status`) VALUES
('933537b3752bf242cca41b9506533dd26aa742e6a596b334e495bef4bbf63b22', 'jelena1ilicc@gmail.com', 'vlada123@gmail.com', '2023-01-26 11:42:17', 10, 'USD', 'SUCCESS'),
('458a33afb23ecc555aa842be973a365970c7f2782fee5b257eb884e2af02c71a', 'jelena1ilicc@gmail.com', 'vlada123@gmail.com', '2023-01-26 11:44:07', 10, 'USD', 'FAIL'),
('270c6ed56573f3711fa8ad442c41e7dcdba091b47bdbd757504b001d51312ac7', 'jelena1ilicc@gmail.com', 'vlada123@gmail.com', '2023-01-26 11:45:16', 10, 'USD', 'FAIL'),
('7b516a19dacb3faef2771957ead13c2d3f0984ac42634666d5a86de3283d55ca', 'jelena1ilicc@gmail.com', 'vlada123@gmail.com', '2023-01-26 11:46:31', 10, 'USD', 'SUCCESS'),
('bcb1d9e61025b762189d1514701336c9f72deab40213837f3c81d9b842c3cba1', 'jelena1ilicc@gmail.com', 'vlada123@gmail.com', '2023-01-26 11:48:12', 10, 'USD', 'SUCCESS'),
('b666719280a3cb2667e3f2cf2223dbefd4f907f10eb197c0dd7ab043f3e5dbc0', 'jelena1ilicc@gmail.com', 'vlada123@gmail.com', '2023-01-26 12:37:45', 10, 'USD', 'SUCCESS');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `firstName` varchar(20) NOT NULL,
  `lastName` varchar(20) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(20) NOT NULL,
  `address` varchar(50) NOT NULL,
  `city` varchar(20) NOT NULL,
  `country` varchar(20) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `balance` double NOT NULL,
  `currency` varchar(10) NOT NULL,
  `isVerified` tinyint(1) NOT NULL
) ;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`firstName`, `lastName`, `email`, `password`, `address`, `city`, `country`, `phone`, `balance`, `currency`, `isVerified`) VALUES
('Jelena', 'Ilic', 'jelena1ilicc@gmail.com', '123', 'Dr Sime Milosevica 10', 'Novi Sad', 'Srbija', '0611747103', 130, 'USD', 1),
('Vladimir', 'Stanojevic', 'vlada123@gmail.com', '123', 'Novosadskog sajma 5', 'Novi Sad', 'Srbija', '0611589654', 20, 'USD', 1);

-- --------------------------------------------------------

--
-- Table structure for table `userbalance`
--

CREATE TABLE `userbalance` (
  `email` varchar(50) NOT NULL,
  `currency` varchar(5) NOT NULL,
  `balance` double NOT NULL
) ;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
