from marshmallow import Schema, fields


class UpdatePermissionSchema(Schema):
    can_view = fields.Bool(load_default=True)
    can_edit = fields.Bool(load_default=False)


class UpdateLayoutSchema(Schema):
    layout = fields.List(fields.Dict(), required=True)
