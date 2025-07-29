-- 先检查表是否存在
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'ops_management' 
AND table_name = 'hosts';

-- 如果不存在，创建表
CREATE TABLE IF NOT EXISTS hosts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip VARCHAR(255) NOT NULL,
    system_type VARCHAR(50) NOT NULL,
    protocol VARCHAR(50) NOT NULL,
    port INT NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255),
    description TEXT,
    status VARCHAR(50) DEFAULT 'running',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
); 