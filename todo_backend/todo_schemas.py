from marshmallow import Schema, fields
from marshmallow.validate import Length


class TodoBaseSchema(Schema):
    """
    PUBLIC_INTERFACE
    Base schema for Todo input/output
    """
    title = fields.String(required=True, validate=Length(min=1), metadata={"description": "Short title of the todo"})
    description = fields.String(required=False, allow_none=True, metadata={"description": "Optional description"})


class TodoCreateSchema(TodoBaseSchema):
    """
    PUBLIC_INTERFACE
    Schema for creating a new Todo.
    """
    start_time = fields.DateTime(
        required=False, allow_none=True,
        metadata={"description": "Optional start datetime in ISO8601 format"}
    )


class TodoUpdateSchema(Schema):
    """
    PUBLIC_INTERFACE
    Schema for updating fields on a Todo.
    """
    title = fields.String(required=False, validate=Length(min=1), metadata={"description": "Updated title"})
    description = fields.String(required=False, allow_none=True, metadata={"description": "Updated description"})
    completed = fields.Boolean(required=False, metadata={"description": "Set completion state"})
    start_time = fields.DateTime(required=False, allow_none=True, metadata={"description": "Updated start time"})


class TodoResponseSchema(Schema):
    """
    PUBLIC_INTERFACE
    Schema for returning a Todo item.
    """
    id = fields.Integer()
    title = fields.String()
    description = fields.String(allow_none=True)
    completed = fields.Boolean()
    start_time = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


class TodoListResponseSchema(Schema):
    """
    PUBLIC_INTERFACE
    Schema for returning list of todos.
    """
    items = fields.List(fields.Nested(TodoResponseSchema))
    total = fields.Integer()
