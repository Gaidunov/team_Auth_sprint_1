import click
from flask import Blueprint

from src.core.logger import logger
from src.db.errors import AlreadyExistsError
from src.db.manager import db_manager

commands_bp = Blueprint('commands', __name__)


@commands_bp.cli.command('create-super-user')
@click.argument('name')
@click.password_option()
def create_super_user(name, password):
    try:
        db_manager.utils.create_super_user(name, password)
        logger.info(f'создали  {name}')
        logger.info(f'пароль {password}')
    except AlreadyExistsError:
        logger.info('такой суперюзер уже есть')
