from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))


class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))
