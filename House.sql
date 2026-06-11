CREATE DATABASE House_db;
USE House_db;

-- admin login
CREATE TABLE admin 
(
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- user login
CREATE TABLE users
(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE predictions 
(
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    area DOUBLE NOT NULL,
    bhk INT NOT NULL,
    bathrooms INT NOT NULL,
    location VARCHAR(150) NOT NULL,
    predicted_price DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user
    FOREIGN KEY (user_id) 
    REFERENCES users(user_id)
    ON DELETE CASCADE
);


INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');

select * from predictions;















