#!/usr/bin/env python3
"""
初始化默认应用脚本
确保数据库中有默认的应用模板
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import get_db_connection
import pymysql

def init_default_apps():
    """初始化默认应用模板"""
    
    # 默认应用配置
    default_apps = [
        {
            'id': 'nginx',
            'name': 'Nginx',
            'description': '高性能的HTTP和反向代理web服务器',
            'category': 'web',
            'version': 'latest',
            'tags': ['web', 'proxy', 'server'],
            'deploy_type': 'docker_compose',
            'compose_template': '''version: '3.8'
services:
  nginx:
    image: nginx:${NGINX_VERSION}
    container_name: ${CONTAINER_NAME}
    ports:
      - "${NGINX_PORT}:80"
    volumes:
      - ./config:/etc/nginx/conf.d:ro
      - ./data:/usr/share/nginx/html
      - ./logs:/var/log/nginx
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai''',
            'ports': [
                {'name': 'HTTP', 'host': 8080, 'container': 80, 'protocol': 'tcp'}
            ],
            'volumes': [
                {'name': '配置目录', 'host': 'config', 'container': '/etc/nginx/conf.d'},
                {'name': '网站目录', 'host': 'data', 'container': '/usr/share/nginx/html'},
                {'name': '日志目录', 'host': 'logs', 'container': '/var/log/nginx'}
            ],
            'env_vars': {
                'NGINX_VERSION': {'default': 'latest', 'description': 'Nginx版本', 'required': False},
                'NGINX_PORT': {'default': '8080', 'description': 'HTTP端口', 'required': True}
            },
            'is_system': True
        },
        {
            'id': 'mysql',
            'name': 'MySQL',
            'description': '世界上最流行的开源关系型数据库',
            'category': 'database',
            'version': '8.0',
            'tags': ['database', 'sql', 'mysql'],
            'deploy_type': 'docker_compose',
            'compose_template': '''version: '3.8'
services:
  mysql:
    image: mysql:${MYSQL_VERSION}
    container_name: ${CONTAINER_NAME}
    ports:
      - "${MYSQL_PORT}:3306"
    volumes:
      - ./data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - TZ=Asia/Shanghai
    restart: unless-stopped''',
            'ports': [
                {'name': 'MySQL', 'host': 3306, 'container': 3306, 'protocol': 'tcp'}
            ],
            'volumes': [
                {'name': '数据目录', 'host': 'data', 'container': '/var/lib/mysql'},
                {'name': '配置目录', 'host': 'config', 'container': '/etc/mysql/conf.d'}
            ],
            'env_vars': {
                'MYSQL_VERSION': {'default': '8.0', 'description': 'MySQL版本', 'required': False},
                'MYSQL_PORT': {'default': '3306', 'description': 'MySQL端口', 'required': True},
                'MYSQL_ROOT_PASSWORD': {'default': '123456', 'description': 'Root密码', 'required': True}
            },
            'is_system': True
        },
        {
            'id': 'redis',
            'name': 'Redis',
            'description': '内存中的数据结构存储，用作数据库、缓存和消息代理',
            'category': 'cache',
            'version': '7',
            'tags': ['cache', 'nosql', 'redis'],
            'deploy_type': 'docker_compose',
            'compose_template': '''version: '3.8'
services:
  redis:
    image: redis:${REDIS_VERSION}
    container_name: ${CONTAINER_NAME}
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - ./data:/data
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
    command: redis-server --appendonly yes''',
            'ports': [
                {'name': 'Redis', 'host': 6379, 'container': 6379, 'protocol': 'tcp'}
            ],
            'volumes': [
                {'name': '数据目录', 'host': 'data', 'container': '/data'}
            ],
            'env_vars': {
                'REDIS_VERSION': {'default': '7', 'description': 'Redis版本', 'required': False},
                'REDIS_PORT': {'default': '6379', 'description': 'Redis端口', 'required': True}
            },
            'is_system': True
        },
        {
            'id': 'postgresql',
            'name': 'PostgreSQL',
            'description': '世界上最先进的开源关系型数据库',
            'category': 'database',
            'version': '15',
            'tags': ['database', 'sql', 'postgresql'],
            'deploy_type': 'docker_compose',
            'compose_template': '''version: '3.8'
services:
  postgresql:
    image: postgres:${POSTGRES_VERSION}
    container_name: ${CONTAINER_NAME}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - ./data:/var/lib/postgresql/data
      - ./config:/etc/postgresql
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - TZ=Asia/Shanghai
    restart: unless-stopped''',
            'ports': [
                {'name': 'PostgreSQL', 'host': 5432, 'container': 5432, 'protocol': 'tcp'}
            ],
            'volumes': [
                {'name': '数据目录', 'host': 'data', 'container': '/var/lib/postgresql/data'},
                {'name': '配置目录', 'host': 'config', 'container': '/etc/postgresql'}
            ],
            'env_vars': {
                'POSTGRES_VERSION': {'default': '15', 'description': 'PostgreSQL版本', 'required': False},
                'POSTGRES_PORT': {'default': '5432', 'description': 'PostgreSQL端口', 'required': True},
                'POSTGRES_PASSWORD': {'default': '123456', 'description': '数据库密码', 'required': True}
            },
            'is_system': True
        },
        {
            'id': 'mongodb',
            'name': 'MongoDB',
            'description': '为现代应用程序开发者和云时代构建的文档数据库',
            'category': 'database',
            'version': '7',
            'tags': ['database', 'nosql', 'mongodb'],
            'deploy_type': 'docker_compose',
            'compose_template': '''version: '3.8'
services:
  mongodb:
    image: mongo:${MONGO_VERSION}
    container_name: ${CONTAINER_NAME}
    ports:
      - "${MONGO_PORT}:27017"
    volumes:
      - ./data:/data/db
      - ./config:/data/configdb
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai''',
            'ports': [
                {'name': 'MongoDB', 'host': 27017, 'container': 27017, 'protocol': 'tcp'}
            ],
            'volumes': [
                {'name': '数据目录', 'host': 'data', 'container': '/data/db'},
                {'name': '配置目录', 'host': 'config', 'container': '/data/configdb'}
            ],
            'env_vars': {
                'MONGO_VERSION': {'default': '7', 'description': 'MongoDB版本', 'required': False},
                'MONGO_PORT': {'default': '27017', 'description': 'MongoDB端口', 'required': True}
            },
            'is_system': True
        }
    ]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        print("🚀 开始初始化默认应用模板...")
        
        # 首先确保分类存在
        categories = [
            {'id': 'web', 'name': 'Web服务', 'description': 'Web服务器和反向代理', 'icon': 'globe', 'sort_order': 1},
            {'id': 'database', 'name': '数据库', 'description': '关系型和NoSQL数据库', 'icon': 'database', 'sort_order': 2},
            {'id': 'cache', 'name': '缓存', 'description': '缓存和内存数据库', 'icon': 'zap', 'sort_order': 3},
            {'id': 'monitor', 'name': '监控', 'description': '监控和日志收集工具', 'icon': 'chart-bar', 'sort_order': 4},
            {'id': 'dev', 'name': '开发工具', 'description': '开发和构建工具', 'icon': 'code', 'sort_order': 5},
            {'id': 'other', 'name': '其他', 'description': '其他应用', 'icon': 'dots-horizontal', 'sort_order': 99}
        ]
        
        for category in categories:
            cursor.execute("""
                INSERT INTO app_categories (id, name, description, icon, sort_order)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                description = VALUES(description),
                icon = VALUES(icon),
                sort_order = VALUES(sort_order)
            """, (category['id'], category['name'], category['description'], category['icon'], category['sort_order']))
        
        # 插入默认应用
        inserted_count = 0
        updated_count = 0
        
        for app in default_apps:
            # 检查应用是否已存在
            cursor.execute("SELECT id FROM app_templates WHERE id = %s", (app['id'],))
            exists = cursor.fetchone()
            
            if exists:
                # 更新现有应用
                cursor.execute("""
                    UPDATE app_templates SET
                    name = %s, description = %s, category = %s, version = %s,
                    tags = %s, deploy_type = %s, compose_template = %s,
                    services = %s, ports = %s, volumes = %s, env_vars = %s,
                    status = 'active', is_system = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    app['name'], app['description'], app['category'], app['version'],
                    json.dumps(app['tags']), app['deploy_type'], app['compose_template'],
                    json.dumps({}), json.dumps(app['ports']), json.dumps(app['volumes']),
                    json.dumps(app['env_vars']), app['is_system'], app['id']
                ))
                updated_count += 1
                print(f"✅ 更新应用: {app['name']}")
            else:
                # 插入新应用
                cursor.execute("""
                    INSERT INTO app_templates (
                        id, name, description, category, version, tags,
                        deploy_type, compose_template, services, ports, volumes, env_vars,
                        status, is_system
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    app['id'], app['name'], app['description'], app['category'], app['version'],
                    json.dumps(app['tags']), app['deploy_type'], app['compose_template'],
                    json.dumps({}), json.dumps(app['ports']), json.dumps(app['volumes']),
                    json.dumps(app['env_vars']), 'active', app['is_system']
                ))
                inserted_count += 1
                print(f"✅ 新增应用: {app['name']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🎉 默认应用初始化完成!")
        print(f"📊 统计: 新增 {inserted_count} 个，更新 {updated_count} 个")
        print(f"📋 应用列表:")
        for app in default_apps:
            print(f"  • {app['name']} ({app['id']}) - {app['category']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_default_apps()