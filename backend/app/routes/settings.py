from flask import Blueprint, request, jsonify
from app.utils.auth import login_required
from app.utils.database import get_db_connection
import json  # 添加 json 导入

settings = Blueprint('settings', __name__)

@settings.route('/api/settings/notification', methods=['GET', 'POST'])
@login_required
def notification_settings():
    db = get_db_connection()
    if request.method == 'GET':
        try:
            with db.cursor() as cursor:
                cursor.execute('SELECT * FROM notification_settings WHERE id = 1')
                settings = cursor.fetchone()
            
            if settings is None:
                return jsonify({
                    'success': True,
                    'data': {
                        'enabled': True,
                        'methods': {'email': True, 'sms': False},
                        'levels': {'error': True, 'warning': True, 'info': False}
                    }
                })
            
            # 从数据库读取时将JSON字符串转换回字典
            return jsonify({
                'success': True,
                'data': {
                    'enabled': bool(settings['enabled']),
                    'methods': json.loads(settings['methods']),
                    'levels': json.loads(settings['levels'])
                }
            })
        finally:
            db.close()
    
    data = request.get_json()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'REPLACE INTO notification_settings (id, enabled, methods, levels) VALUES (%s, %s, %s, %s)',
                (
                    1, 
                    data['enabled'],
                    json.dumps(data['methods']),  # 将字典转换为JSON字符串
                    json.dumps(data['levels'])    # 将字典转换为JSON字符串
                )
            )
        db.commit()
        return jsonify({'success': True, 'message': '保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@settings.route('/api/settings/aliyun', methods=['GET', 'POST'])
@login_required
def aliyun_settings():
    db = get_db_connection()
    if request.method == 'GET':
        try:
            with db.cursor() as cursor:
                cursor.execute('SELECT * FROM aliyun_settings WHERE id = 1')
                settings = cursor.fetchone()
            
            if settings is None:
                return jsonify({
                    'success': True,
                    'data': {
                        'accessKeyId': '',
                        'accessKeySecret': ''
                    }
                })
                
            return jsonify({
                'success': True,
                'data': {
                    'accessKeyId': settings['access_key_id'],
                    'accessKeySecret': ''
                }
            })
        finally:
            db.close()
    
    data = request.get_json()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'REPLACE INTO aliyun_settings (id, access_key_id, access_key_secret, region) VALUES (%s, %s, %s, %s)',
                (1, data['accessKeyId'], data['accessKeySecret'], 'cn-hangzhou')
            )
        db.commit()
        return jsonify({'success': True, 'message': '保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@settings.route('/api/settings/mail', methods=['GET', 'POST'])
@login_required
def mail_settings():
    db = get_db_connection()
    if request.method == 'GET':
        try:
            with db.cursor() as cursor:
                cursor.execute('SELECT * FROM mail_settings WHERE id = 1')
                settings = cursor.fetchone()
            
            if settings is None:
                return jsonify({
                    'success': True,
                    'data': {
                        'smtpServer': '',
                        'smtpPort': 587,
                        'senderEmail': '',
                        'useTLS': True
                    }
                })
                
            return jsonify({
                'success': True,
                'data': {
                    'smtpServer': settings['smtp_server'],
                    'smtpPort': settings['smtp_port'],
                    'senderEmail': settings['sender_email'],
                    'useTLS': settings['use_tls']
                }
            })
        finally:
            db.close()
    
    data = request.get_json()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'REPLACE INTO mail_settings (id, smtp_server, smtp_port, sender_email, password, use_tls) VALUES (%s, %s, %s, %s, %s, %s)',
                (1, data['smtpServer'], data['smtpPort'], data['senderEmail'], data['password'], data['useTLS'])
            )
        db.commit()
        return jsonify({'success': True, 'message': '保存成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@settings.route('/api/settings/mail/test', methods=['POST'])
@login_required
def test_mail_connection():
    data = request.get_json()
    try:
        # TODO: 实现邮件连接测试逻辑
        return jsonify({'success': True, 'message': '连接测试成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@settings.route('/api/settings/jenkins', methods=['GET', 'POST'])
@login_required
def jenkins_settings():
    db = get_db_connection()
    if request.method == 'GET':
        try:
            with db.cursor() as cursor:
                cursor.execute('SELECT * FROM jenkins_settings ORDER BY id')
                instances = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': [{
                    'id': instance['id'],
                    'name': instance['name'],
                    'url': instance['url'],
                    'username': instance['username'],
                    'enabled': bool(instance['enabled'])
                } for instance in instances]
            })
        finally:
            db.close()
    
    data = request.get_json()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'INSERT INTO jenkins_settings (name, url, username, token, enabled) VALUES (%s, %s, %s, %s, %s)',
                (data['name'], data['url'], data['username'], data['token'], data.get('enabled', True))
            )
        db.commit()
        return jsonify({'success': True, 'message': 'Jenkins实例添加成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        db.close()

@settings.route('/api/settings/jenkins/<int:instance_id>', methods=['PUT', 'DELETE'])
@login_required
def jenkins_instance(instance_id):
    db = get_db_connection()
    
    if request.method == 'PUT':
        data = request.get_json()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    'UPDATE jenkins_settings SET name=%s, url=%s, username=%s, token=%s, enabled=%s WHERE id=%s',
                    (data['name'], data['url'], data['username'], data['token'], data.get('enabled', True), instance_id)
                )
            db.commit()
            return jsonify({'success': True, 'message': 'Jenkins实例更新成功'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            db.close()
    
    elif request.method == 'DELETE':
        try:
            with db.cursor() as cursor:
                cursor.execute('DELETE FROM jenkins_settings WHERE id=%s', (instance_id,))
            db.commit()
            return jsonify({'success': True, 'message': 'Jenkins实例删除成功'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            db.close()

@settings.route('/notification_methods', methods=['GET'])
def get_notification_methods():
    """获取所有通知方式"""
    try:
        sql = """
            SELECT id, type, name, enabled 
            FROM settings 
            WHERE category = 'notification'
        """
        result = db.fetch_all(sql)
        return jsonify({
            'code': 200,
            'data': [{
                'id': row['id'],
                'type': row['type'], 
                'name': row['name'],
                'enabled': bool(row['enabled'])
            } for row in result]
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取通知方式失败: {str(e)}'
        }) 