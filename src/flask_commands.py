import click
from flask import Blueprint
from src.db.manager import db_manager
from src.db.errors import AlreadyExistsError


commands_bp = Blueprint('commands', __name__)


@commands_bp.cli.command('create-super-user')
@click.argument('name')
@click.password_option()
def create_super_user(name, password):
    try:
        db_manager.utils.create_super_user(name, password)
        print('создали ', name)
        print('пароль', password)
    except AlreadyExistsError:
        print('такой суперюзер уже есть')
