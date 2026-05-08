from marshmallow import Schema, fields, validate


class CreateFamilySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))


class ChangeRoleSchema(Schema):
    role_name = fields.Str(required=True, validate=validate.OneOf(['Familyadmin', 'Guest']))


class JoinByCodeSchema(Schema):
    code = fields.Str(required=True, validate=validate.Length(min=1))
