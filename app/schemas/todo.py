from marshmallow import Schema, fields, validate


class CreateTodoSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(load_default=None)


class UpdateTodoSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str()
    is_completed = fields.Bool()
