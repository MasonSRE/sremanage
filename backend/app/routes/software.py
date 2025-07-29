import pymysql
from flask import Blueprint, request, jsonify
from app.utils.database import get_db
from app.utils.auth import login_required

bp = Blueprint('software', __name__, url_prefix='/api/software')

@bp.route('/packages', methods=['GET'])
@login_required
def get_packages():
    """获取所有软件包列表"""
    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT id, name, version, description FROM software_packages"
            )
            packages = cursor.fetchall()
            
            return jsonify({
                'success': True,
                'data': packages  # 因为使用了DictCursor，这里直接返回结果即可
            })
        except pymysql.Error as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

@bp.route('/packages', methods=['POST'])
@login_required
def add_package():
    """添加新的软件包"""
    data = request.get_json()
    
    if not all(key in data for key in ['name', 'version', 'description']):
        return jsonify({
            'success': False,
            'message': '缺少必要的字段'
        }), 400
    
    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(
                """
                INSERT INTO software_packages (name, version, description)
                VALUES (?, ?, ?)
                """,
                (data['name'], data['version'], data['description'])
            )
            db.commit()
            
            return jsonify({
                'success': True,
                'message': '软件包添加成功'
            })
        except pymysql.Error as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

@bp.route('/install', methods=['POST'])
@login_required
def install_software():
    """在指定主机上安装软件"""
    data = request.get_json()
    
    if not all(key in data for key in ['host_id', 'package_id']):
        return jsonify({
            'success': False,
            'message': '缺少必要的字段'
        }), 400
    
    db = get_db()
    with db.cursor() as cursor:
        try:
            # 检查软件包是否存在
            cursor.execute(
                "SELECT version FROM software_packages WHERE id = %s",
                (data['package_id'],)
            )
            package = cursor.fetchone()
            if not package:
                return jsonify({
                    'success': False,
                    'message': '软件包不存在'
                }), 404
            
            # 记录安装信息
            cursor.execute(
                """
                INSERT INTO software_installations 
                (host_id, package_id, version, status)
                VALUES (%s, %s, %s, 'installed')
                """,
                (data['host_id'], data['package_id'], package[0])
            )
            db.commit()
            
            return jsonify({
                'success': True,
                'message': '软件安装成功'
            })
        except pymysql.Error as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

@bp.route('/check-updates', methods=['GET'])
@login_required
def check_updates():
    """检查所有已安装软件的更新状态"""
    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(
                """
                SELECT 
                    h.id as host_id,
                    h.hostname,
                    sp.id as package_id,
                    sp.name as package_name,
                    si.version as current_version,
                    sp.version as latest_version
                FROM software_installations si
                JOIN hosts h ON h.id = si.host_id
                JOIN software_packages sp ON sp.id = si.package_id
                WHERE si.status = 'installed'
                """
            )
            installations = cursor.fetchall()
            
            updates = []
            for inst in installations:
                status = 'uptodate'
                if inst[4] != inst[5]:  # current_version != latest_version
                    status = 'available'
                
                updates.append({
                    'host_id': inst[0],
                    'hostname': inst[1],
                    'package_id': inst[2],
                    'package_name': inst[3],
                    'current_version': inst[4],
                    'latest_version': inst[5],
                    'status': status
                })
            
            return jsonify({
                'success': True,
                'data': updates
            })
        except pymysql.Error as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

@bp.route('/update', methods=['POST'])
@login_required
def update_software():
    """更新指定主机上的软件"""
    data = request.get_json()
    
    if not all(key in data for key in ['host_id', 'package_id']):
        return jsonify({
            'success': False,
            'message': '缺少必要的字段'
        }), 400
    
    db = get_db()
    with db.cursor() as cursor:
        try:
            # 获取最新版本
            cursor.execute(
                "SELECT version FROM software_packages WHERE id = %s",
                (data['package_id'],)
            )
            package = cursor.fetchone()
            if not package:
                return jsonify({
                    'success': False,
                    'message': '软件包不存在'
                }), 404
            
            # 更新安装记录
            cursor.execute(
                """
                UPDATE software_installations
                SET version = %s, status = 'installed', updated_at = CURRENT_TIMESTAMP
                WHERE host_id = %s AND package_id = %s
                """,
                (package[0], data['host_id'], data['package_id'])
            )
            db.commit()
            
            return jsonify({
                'success': True,
                'message': '软件更新成功'
            })
        except pymysql.Error as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500 