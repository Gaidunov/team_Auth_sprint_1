from spectree import SpecTree
from pydantic import BaseModel, Field

class Profile(BaseModel):
    login:str
    password: str = Field(alias='pass')

class ChPass(BaseModel):
    login:str
    password: str = Field(alias='pass')
    newpassword: str = Field(alias='new_pass')

class Query(BaseModel):
    login:str = None
    password: str = Field(alias='pass', default=None) 
    newpassword: str = Field(alias='new_pass', default=None)  

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