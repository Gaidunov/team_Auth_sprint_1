from pydantic import BaseModel, Field

from openapi_schema_pydantic import OpenAPI
from openapi_schema_pydantic.util import PydanticSchema, construct_open_api_with_schema_class

def construct_base_open_api() -> OpenAPI:
    return OpenAPI.parse_obj({
        "info": {"title": "AUTH API", "version": "v0.0.1"},
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {"content": {"application/json": {
                        "schema": PydanticSchema(schema_class=PingRequest)
                    }}},
                    "responses": {"200": {
                        "description": "pong",
                        "content": {"application/json": {
                            "schema": PydanticSchema(schema_class=PingResponse)
                        }},
                    }},
                }
            }
        },
    })

class PingRequest(BaseModel):
    """Ping Request"""
    req_foo: str = Field(description="foo value of the request")
    req_bar: str = Field(description="bar value of the request")

class PingResponse(BaseModel):
    """Ping response"""
    resp_foo: str = Field(description="foo value of the response")
    resp_bar: str = Field(description="bar value of the response")

open_api = construct_base_open_api()
open_api = construct_open_api_with_schema_class(open_api)

# print the result openapi.json
print(open_api.json(by_alias=True, exclude_none=True, indent=2))