-- SQL Setup DDL for Hostel Management System (HMS)

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS hostel_management;
USE hostel_management;

-- 1. Table: Room_Types
CREATE TABLE IF NOT EXISTS Room_Types (
    room_type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(255) NOT NULL,
    semester_base_price DECIMAL(10,2) NOT NULL,
    inventory_assets JSON NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Table: Rooms
CREATE TABLE IF NOT EXISTS Rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_type_id INT NOT NULL,
    room_number VARCHAR(50) NOT NULL UNIQUE,
    floor_assignment VARCHAR(50) NOT NULL,
    total_capacity INT NOT NULL,
    current_occupancy INT NOT NULL DEFAULT 0,
    room_status VARCHAR(50) NOT NULL DEFAULT 'Vacant',
    FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Table: Residents
CREATE TABLE IF NOT EXISTS Residents (
    resident_id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    student_id VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    academic_major VARCHAR(255) NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    deposit_paid DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    hostel_tuition_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    academic_tuition_debt DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    allocation_status VARCHAR(100) NOT NULL DEFAULT 'Fully Registered',
    probation_reason TEXT NULL,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indexes for performance optimization
CREATE INDEX idx_rooms_status ON Rooms(room_status);
CREATE INDEX idx_residents_student_id ON Residents(student_id);
CREATE INDEX idx_residents_room_id ON Residents(room_id);
