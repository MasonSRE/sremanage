-- 创建软件包表
CREATE TABLE IF NOT EXISTS software_packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建软件安装记录表
CREATE TABLE IF NOT EXISTS software_installations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT NOT NULL,
    package_id INT NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'installed',
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES hosts(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES software_packages(id) ON DELETE CASCADE
);

-- 添加索引以提高查询性能
CREATE INDEX idx_software_installations_host ON software_installations(host_id);
CREATE INDEX idx_software_installations_package ON software_installations(package_id); 