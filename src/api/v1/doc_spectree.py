from spectree import SpecTree, Response
from pydantic import BaseModel, Field, constr

class Profile(BaseModel):
    name: constr(min_length=2, max_length=40)  # constrained str
    age: int = Field(..., gt=0, lt=150, description="user age(Human)")

    class Config:
        schema_extra = {
            # provide an example
            "example": {
                "name": "very_important_user",
                "age": 42,
            }
        }

class Message(BaseModel):
    text: str

spec = SpecTree("flask")