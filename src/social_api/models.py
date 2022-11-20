from pydantic import BaseModel


class VkAccessResponse(BaseModel):
    access_token:str
    expires_in:int 
    user_id:int
    email:str