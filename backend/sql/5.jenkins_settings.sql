-- Jenkins设置表
CREATE TABLE IF NOT EXISTS jenkins_settings (
    id INTEGER AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    username VARCHAR(100) NOT NULL,
    token TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 插入示例数据（可选）
-- INSERT INTO jenkins_settings (name, url, username, token, enabled) 
-- VALUES ('示例Jenkins', 'https://jenkins.example.com', 'admin', 'your-api-token-here', 1);