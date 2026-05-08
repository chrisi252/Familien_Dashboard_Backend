from marshmallow import Schema, fields, validate


class CreateEntrySchema(Schema):
    person_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    subject = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    weekday = fields.Int(required=True, validate=validate.Range(min=0, max=4))
    start_time = fields.Str(required=True, validate=validate.Length(min=1))
    end_time = fields.Str(required=True, validate=validate.Length(min=1))
    color = fields.Str()
    room = fields.Str(allow_none=True)
    teacher = fields.Str(allow_none=True)
    note = fields.Str(allow_none=True)


class UpdateEntrySchema(Schema):
    person_name = fields.Str(validate=validate.Length(min=1, max=255))
    subject = fields.Str(validate=validate.Length(min=1, max=255))
    weekday = fields.Int(validate=validate.Range(min=0, max=4))
    start_time = fields.Str()
    end_time = fields.Str()
    color = fields.Str()
    room = fields.Str(allow_none=True)
    teacher = fields.Str(allow_none=True)
    note = fields.Str(allow_none=True)
