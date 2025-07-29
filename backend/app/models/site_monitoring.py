from app.extensions import db
from datetime import datetime

class SiteMonitoring(db.Model):
    __tablename__ = 'site_monitoring'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(255), nullable=False)
    site_url = db.Column(db.String(500), nullable=False)
    check_interval = db.Column(db.Integer, default=300)  # 检查间隔（秒）
    timeout = db.Column(db.Integer, default=30)  # 超时时间（秒）
    enabled = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='unknown')  # online, offline, unknown
    last_check_time = db.Column(db.DateTime)
    last_response_time = db.Column(db.Integer)  # 响应时间（毫秒）
    failure_count = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, site_name, site_url, check_interval=300, timeout=30, enabled=True, description=None):
        self.site_name = site_name
        self.site_url = site_url
        self.check_interval = check_interval
        self.timeout = timeout
        self.enabled = enabled
        self.description = description

    def to_dict(self):
        return {
            'id': self.id,
            'site_name': self.site_name,
            'site_url': self.site_url,
            'check_interval': self.check_interval,
            'timeout': self.timeout,
            'enabled': self.enabled,
            'status': self.status,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'last_response_time': self.last_response_time,
            'failure_count': self.failure_count,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SiteMonitoringHistory(db.Model):
    __tablename__ = 'site_monitoring_history'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site_monitoring.id'), nullable=False)
    check_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # online, offline, timeout, error
    response_time = db.Column(db.Integer)  # 响应时间（毫秒）
    http_code = db.Column(db.Integer)  # HTTP状态码
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, site_id, check_time, status, response_time=None, http_code=None, error_message=None):
        self.site_id = site_id
        self.check_time = check_time
        self.status = status
        self.response_time = response_time
        self.http_code = http_code
        self.error_message = error_message

    def to_dict(self):
        return {
            'id': self.id,
            'site_id': self.site_id,
            'check_time': self.check_time.isoformat() if self.check_time else None,
            'status': self.status,
            'response_time': self.response_time,
            'http_code': self.http_code,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }