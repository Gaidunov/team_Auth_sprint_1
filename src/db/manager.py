import uuid
from datetime import datetime
import string
from secrets import choice as secrets_choice

from sqlalchemy.orm import Session

from src.core.logger import logger
from src.db import errors
from src.db.db import db_session
from src.db.utils import get_device_from_user_agent
from src.models.models import User, Role, SessionHistory, RegService
from src.models.schemas import PydanticRole, PydanticSessions


class RegServiceManager:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_redirect_url(self, service):
        existing_url = self.session.query(RegService).filter_by(name_service=service).first()
        if not existing_url:
            raise errors.CustomNotFoundError(reason=f'service {service}')
        return existing_url


class UserManager:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.session_history_schema = PydanticSessions

    @staticmethod
    def _generate_random_pass()->str:
        """генерим рандомный пароль для юзеров, регающихся через соцсети"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets_choice(alphabet) for _ in range(16)) 

    def register_via_vk(self, login):
        password = self._generate_random_pass()
        #TODO заджейсонить респонсы?
        try:
            self.register_user(login, password)
            msg = f'зарегали юзера. вот пароль {password}'
        except errors.AlreadyExistsError:
            user = self.get_user_by_login(login)
            msg = f'залогинили юзера. вот юзер {user}'
        return msg

    def get_user_by_login(self, login: str) -> User:
        existing_user = self.session.query(User).filter_by(login=login).first()
        if not existing_user:
            raise errors.CustomNotFoundError(reason=f'user {login}')
        return existing_user

    def get_user_by_id(self, user_id: str) -> User:
        existing_user = self.session.query(User).filter_by(id=user_id).first()
        if not existing_user:
            raise errors.CustomNotFoundError(user_id)
        return existing_user

    def change_password(
        self,
        login: str,
        password: str,
        new_password: str
    ):
        user = self.get_user_by_login(login)
        if user.check_password(password):
            user.set_password(new_password)
            self.session.add(user)
            self.session.commit()
        else:
            raise errors.Forbidden('неправильный пароль')

    def register_user(self, login: str, password: str) -> User:
        query = self.session.query(User)
        user = query.filter_by(login=login).first()
        if user:
            raise errors.AlreadyExistsError(f'user {login}')
        if not user:
            id_=uuid.uuid4()
            user = User(id=id_, login=login)
            user.set_password(password)
            self.session.add(user)
            self.session.commit()
        return user

    def login_user(
        self,
        login: str,
        password: str,
        user_agent: str
    ) -> User | None:
        query = self.session.query(User)
        user = query.filter_by(login=login).first()
        device = get_device_from_user_agent(user_agent)

        if not user:
            raise errors.CustomNotFoundError(f'user {login}')
        if user.check_password(password):
            session_action = SessionHistory(
                id=str(uuid.uuid1()),
                user_id=user.id,
                user_agent=user_agent,
                action='login',
                date=datetime.now(),
                user_device_type=device,
            )
            self.session.add(session_action)
            self.session.commit()
            return user
        raise errors.Forbidden('неправильный пароль')

    def get_user_sessions(self, login: str) -> list[str] | None:
        user = self.get_user_by_login(login)
        sessions = self.session.query(
            SessionHistory).filter_by(user_id=user.id).all()
        if not sessions:
            return []
        parsed_sessions = [self.session_history_schema.from_orm(
            sess).json() for sess in sessions]
        return parsed_sessions

    def logout_user(self, login, user_agent):
        user = self.get_user_by_login(login)
        session_action = SessionHistory(
            id=str(uuid.uuid1()),
            user_id=user.id,
            user_agent=user_agent,
            action='logout',
            date=datetime.now()
        )
        self.session.add(session_action)
        self.session.commit()


class RoleManager(UserManager):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.session = session
        self.role_schema = PydanticRole

    def add_role(self, role_name):
        try:
            role = self.get_role_by_name(role_name)
            if role:
                raise errors.AlreadyExistsError(f'роль "{role_name}"')

        except errors.CustomNotFoundError:
            role = Role(id=str(uuid.uuid1()), name=role_name)
            self.session.add(role)
            self.session.commit()
            return f'роль {role_name} добавлена'

    def get_user_roles_by_id(self, user_id: str) -> list[str] | None:
        self.session_history_schema = SessionHistory
        user = self.get_user_by_id(user_id)
        return user.roles

    def get_user_roles_by_login(self, login: str) -> list[str] | None:
        user = self.get_user_by_login(login)
        if not user.roles:
            return []

        parsed_roles = [
            self.role_schema.from_orm(role).name
            for role in user.roles
        ]
        return parsed_roles

    def get_role_by_name(self, role_name: str) -> Role | None:
        role = self.session.query(Role).filter_by(name=role_name).first()
        if not role:
            raise errors.CustomNotFoundError(f'role_name {role_name}')
        return role

    def add_user_a_role(self, login: str, role_name: str):
        user = self.get_user_by_login(login)
        role = self.get_role_by_name(role_name)

        user_rolser_parsed = [
            self.role_schema.from_orm(user_role).name
            for user_role in user.roles
        ]

        if role_name in user_rolser_parsed:
            raise errors.AlreadyExistsError(
                f'у юзера {login} уже есть роль {role_name}. '
            )

        user.roles.append(role)
        self.session.add(user)
        self.session.commit()
        return f'добавили {role} юзеру {login}'

    def remove_role_from_user(self, login: str, role_name: str):
        user = self.get_user_by_login(login)
        role = self.get_role_by_name(role_name)
        user_rolser_parsed = [self.role_schema.from_orm(
            user_role).name for user_role in user.roles]
        if role_name not in user_rolser_parsed:
            raise errors.CustomNotFoundError(
                f'у юзера {login} нет роли {role_name} )')
        user.roles.remove(role)
        self.session.add(user)
        self.session.commit()
        return f'удалили {role_name} юзеру {login}'

    def rename_role(self, role_name, new_role_name):
        role = self.get_role_by_name(role_name)
        role.name = new_role_name
        self.session.add(role)
        self.session.commit()
        return f'переименовали роль {role_name} на {new_role_name}'

    def get_all_roles(self):
        roles = self.session.query(Role).all()
        if not roles:
            return roles
        roles = [self.role_schema.from_orm(role).name for role in roles]
        return roles


class Utils(RoleManager):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.session = session

    def create_super_user(self, name, password):
        new_super_user = self.register_user(name, password)
        self.add_user_a_role(new_super_user.login, role_name='superuser')

    def prepopulate_db(self):
        roles = ['superuser', 'user']
        for r in roles:
            try:
                self.add_role(r)
            except Exception as ex:
                logger.info(ex)


class DataBaseManager:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserManager(session)
        self.roles = RoleManager(session)
        self.reg_servise = RegServiceManager(session)
        self.utils = Utils(session)


db_manager = DataBaseManager(db_session)
