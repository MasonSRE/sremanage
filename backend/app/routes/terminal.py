from flask import Blueprint, request
from flask_sock import Sock
import paramiko
import threading
import select
import time
from app.utils.database import get_db_connection
from app.utils.logger import logger

# 创建一个新的 Sock 实例
sock = Sock()

terminal_bp = Blueprint('terminal', __name__)  # 移除 url_prefix

@sock.route('/api/terminal')  # 修改路由路径
def ssh_terminal(ws):
    try:
        logger.info("=== WebSocket连接开始 ===")
        logger.info(f"请求参数: {request.args}")
        logger.info(f"请求头: {request.headers}")
        
        # 添加日志
        logger.info("收到终端连接请求")
        logger.info(f"连接参数: {request.args}")
        
        # 获取连接参数
        host = request.args.get('host')
        port = int(request.args.get('port', 22))
        username = request.args.get('username')
        instance_id = request.args.get('instance_id')  # 阿里云实例ID
        provider = request.args.get('provider')  # 云服务商标识
        
        if not all([host, username]):
            logger.error("缺少必要的连接参数")
            ws.send('Error: Missing required connection parameters\r\n')
            return
            
        # 从数据库获取密码
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            password = None
            
            # 如果是阿里云实例，从aliyun_instance_config表获取密码
            if provider == 'aliyun' and instance_id:
                logger.info(f"查找阿里云实例配置: {instance_id}")
                cursor.execute("SELECT password FROM aliyun_instance_config WHERE instance_id = %s", (instance_id,))
                result = cursor.fetchone()
                if result and result['password']:
                    password = result['password']
                    logger.info("成功获取阿里云实例密码")
                else:
                    logger.warning(f"阿里云实例 {instance_id} 没有配置密码")
            
            # 如果没有找到密码，尝试从手动添加的主机表查找
            if not password:
                logger.info("尝试从手动主机表查找密码")
                cursor.execute("SELECT password FROM hosts WHERE ip = %s AND username = %s", (host, username))
                result = cursor.fetchone()
                if result and result['password']:
                    password = result['password']
                    logger.info("成功从手动主机表获取密码")
            
            cursor.close()
            conn.close()
            
            if not password:
                logger.error(f"未找到主机凭据: {host}, 用户: {username}, 实例ID: {instance_id}")
                if provider == 'aliyun':
                    ws.send('Authentication failed: 请先在阿里云实例编辑对话框中配置登录密码\r\n')
                else:
                    ws.send('Authentication failed: Invalid credentials\r\n')
                return
        except Exception as e:
            logger.error(f"数据库查询失败: {str(e)}")
            ws.send(f"Database error: {str(e)}\r\n")
            return

        # 创建SSH客户端
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            logger.info(f"尝试连接到主机: {host}")
            ssh.connect(host, port, username, password)
            logger.info(f"成功连接到主机: {host}")
            
            # 获取SSH通道
            channel = ssh.invoke_shell()
            
            # 创建双向数据传输
            def ssh_to_ws():
                while True:
                    if channel.exit_status_ready():
                        break
                    try:
                        r, w, e = select.select([channel], [], [], 0.1)
                        if r:
                            data = channel.recv(1024)
                            if not data:
                                break
                            ws.send(data.decode())
                    except Exception as e:
                        logger.error(f"SSH读取错误: {str(e)}")
                        break
                    
            thread = threading.Thread(target=ssh_to_ws)
            thread.daemon = True
            thread.start()
            
            # 处理WebSocket消息
            while True:
                try:
                    data = ws.receive()
                    if data.startswith('resize:'):
                        rows, cols = map(int, data[7:].split(','))
                        channel.resize_pty(width=cols, height=rows)
                    else:
                        channel.send(data)
                except Exception as e:
                    logger.error(f"WebSocket错误: {str(e)}")
                    break
                
        except Exception as e:
            logger.error(f"SSH连接错误: {str(e)}")
            ws.send(f"SSH connection error: {str(e)}\r\n")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}", exc_info=True)
        ws.send(f"Error: {str(e)}\r\n")
    finally:
        logger.info("=== WebSocket连接结束 ===")
        if 'channel' in locals():
            channel.close()
        if 'ssh' in locals():
            ssh.close() 