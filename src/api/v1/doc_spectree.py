from spectree import SpecTree, Response
from pydantic import BaseModel, Field, constr

class Profile(BaseModel):
    login:str
    password: str = Field(alias='pass')

class ChPass(BaseModel):
    login:str
    password: str = Field(alias='pass')
    newpassword: str = Field(alias='new_pass')

class QueryLogin(BaseModel):
    login:str

class QueryRegService(BaseModel):
    servise:str

class Cookies(BaseModel):
    access_token_cookie:str
    refresh_token_cookie:str

class Role(BaseModel):
    role: str

class RoleLogin(BaseModel):
    role: str
    login: str

class RenRole(BaseModel):
    role: str
    new_name_role_name: str

spec = SpecTree("flask")