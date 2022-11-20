from spectree import SpecTree
from pydantic import BaseModel, Field


class ChPass(BaseModel):
    login: str
    password: str = Field(alias='pass')
    newpassword: str = Field(alias='new_pass')


class Login(BaseModel):
    login: str = None
    password: str = Field(alias='pass', default=None) 


class Cookies(BaseModel):
    access_token_cookie:str = None
    refresh_token_cookie:str = None


class Role(BaseModel):
    role: str


class RoleLogin(BaseModel):
    role: str
    login: str


class RenRole(BaseModel):
    role: str
    new_name_role_name: str


spec = SpecTree("flask")
