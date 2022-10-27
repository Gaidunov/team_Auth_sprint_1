from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow_enum import EnumField
from marshmallow import post_load

from src.models.models import Role


#[{'users': ['93b7d494-5606-11ed-a5c3-00155d5c5872'], 'name': <UserRoles.registered: 'registred'>, 'id': '3'}]

class RoleSchema(SQLAlchemySchema):
    class Meta:
        model = Role
        include_relationships = True
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()
    name = auto_field()
    users = auto_field()

# role_schema = Role()
# dict_ = {"admin":UserRoles.admin}
# role =
#  role_schema.dumps(dict_) -> str
#role_schema.dump(dict_) -> dict

# print(type(role))

# print(dir(role))
# class ArtistSchema(Schema):
#     name = fields.Str()


# class AlbumSchema(Schema):
#     title = fields.Str()
#     release_date = fields.Date()
#     artist = fields.Nested(ArtistSchema())


# bowie = dict(name="David Bowie")
# album = dict(artist=bowie, title="Hunky Dory", release_date=date(1971, 12, 17))

# schema = AlbumSchema()
# result = schema.dump(album)
# pprint(result, indent=2)