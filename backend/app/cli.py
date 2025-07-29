import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models.user import User

@click.command('create-admin')
@click.option('--username', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--email', prompt=True)
@with_appcontext
def create_admin(username, password, email):
    """创建管理员用户"""
    if User.query.filter_by(username=username).first():
        click.echo(f'用户 {username} 已存在!')
        return
    
    admin = User(
        username=username,
        password=password,
        email=email
    )
    db.session.add(admin)
    db.session.commit()
    click.echo(f'管理员用户 {username} 创建成功!') 