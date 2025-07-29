-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(120),
    role VARCHAR(20) DEFAULT 'user',
    status BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入管理员用户
INSERT INTO users (username, password, email, role, status) 
VALUES ('admin', '9itNKA6nVs0ZkGw321Tu', 'admin@example.com', 'admin', 1)
ON DUPLICATE KEY UPDATE 
    password = VALUES(password),
    email = VALUES(email),
    role = VALUES(role),
    status = VALUES(status); 