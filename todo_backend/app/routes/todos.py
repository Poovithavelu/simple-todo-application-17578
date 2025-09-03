from datetime import datetime
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..models import db, Todo
from ...todo_schemas import (
    TodoCreateSchema,
    TodoUpdateSchema,
    TodoResponseSchema,
    TodoListResponseSchema,
)

blp = Blueprint(
    "Todos",
    "todos",
    url_prefix="/api/todos",
    description="CRUD endpoints for managing todos",
)


@blp.route("/")
class TodosCollection(MethodView):
    """
    PUBLIC_INTERFACE
    GET: List todos (optionally filter by completed).
    POST: Create a new todo.

    Query params:
    - completed: Optional boolean to filter by completion state.

    Responses:
    - 200 for list
    - 201 for created
    """
    @blp.arguments(schema=None, location="query")
    @blp.response(200, TodoListResponseSchema)
    @blp.doc(summary="List todos", description="List all todos with optional 'completed' filter.")
    def get(self, args=None):
        try:
            query = Todo.query
            completed_param = None
            if args and "completed" in args:
                val = args.get("completed")
                if isinstance(val, str):
                    v = val.lower()
                    if v in ("true", "1", "yes"):
                        completed_param = True
                    elif v in ("false", "0", "no"):
                        completed_param = False
                elif isinstance(val, bool):
                    completed_param = val
            if completed_param is not None:
                query = query.filter(Todo.completed == completed_param)
            items = [t.to_dict() for t in query.order_by(Todo.created_at.desc()).all()]
            return {"items": items, "total": len(items)}
        except SQLAlchemyError as e:
            abort(500, message=f"Database error while listing todos: {str(e)}")

    @blp.arguments(TodoCreateSchema)
    @blp.response(201, TodoResponseSchema)
    @blp.doc(summary="Create todo", description="Create a new todo item.")
    def post(self, json_data):
        try:
            todo = Todo(
                title=json_data["title"],
                description=json_data.get("description"),
                start_time=json_data.get("start_time"),
            )
            db.session.add(todo)
            db.session.commit()
            return todo.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f"Invalid payload: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error while creating todo: {str(e)}")


@blp.route("/<int:todo_id>")
class TodoItem(MethodView):
    """
    PUBLIC_INTERFACE
    GET: Retrieve a single todo
    PUT: Update fields on a todo
    DELETE: Remove a todo
    """
    @blp.response(200, TodoResponseSchema)
    @blp.doc(summary="Get todo", description="Get a single todo by ID.")
    def get(self, todo_id: int):
        todo = Todo.query.get(todo_id)
        if not todo:
            abort(404, message="Todo not found")
        return todo.to_dict()

    @blp.arguments(TodoUpdateSchema)
    @blp.response(200, TodoResponseSchema)
    @blp.doc(summary="Update todo", description="Update title, description, completed, and/or start_time.")
    def put(self, json_data, todo_id: int):
        todo = Todo.query.get(todo_id)
        if not todo:
            abort(404, message="Todo not found")
        try:
            if "title" in json_data:
                todo.title = json_data["title"]
            if "description" in json_data:
                todo.description = json_data["description"]
            if "completed" in json_data:
                todo.completed = bool(json_data["completed"])
            if "start_time" in json_data:
                todo.start_time = json_data["start_time"]
            db.session.commit()
            return todo.to_dict()
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f"Invalid update: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error while updating todo: {str(e)}")

    @blp.response(204)
    @blp.doc(summary="Delete todo", description="Delete a todo by ID.")
    def delete(self, todo_id: int):
        todo = Todo.query.get(todo_id)
        if not todo:
            abort(404, message="Todo not found")
        try:
            db.session.delete(todo)
            db.session.commit()
            return "", 204
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error while deleting todo: {str(e)}")


@blp.route("/<int:todo_id>/toggle")
class TodoToggle(MethodView):
    """
    PUBLIC_INTERFACE
    POST: Toggle completion state of a todo.
    """
    @blp.response(200, TodoResponseSchema)
    @blp.doc(summary="Toggle completed", description="Toggle the 'completed' field and update updated_at.")
    def post(self, todo_id: int):
        todo = Todo.query.get(todo_id)
        if not todo:
            abort(404, message="Todo not found")
        try:
            todo.completed = not todo.completed
            todo.updated_at = datetime.utcnow()
            db.session.commit()
            return todo.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error while toggling todo: {str(e)}")


@blp.route("/<int:todo_id>/start")
class TodoStart(MethodView):
    """
    PUBLIC_INTERFACE
    POST: Set the start_time of a todo to now (or clear when requested).
    """
    @blp.response(200, TodoResponseSchema)
    @blp.doc(
        summary="Set start time",
        description="Set the start_time to current UTC time. Append ?clear=true to remove start_time."
    )
    def post(self, todo_id: int):
        todo = Todo.query.get(todo_id)
        if not todo:
            abort(404, message="Todo not found")

        from flask import request
        clear = request.args.get("clear", "").lower() in ("true", "1", "yes")

        try:
            if clear:
                todo.start_time = None
            else:
                todo.start_time = datetime.utcnow()
            db.session.commit()
            return todo.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error while updating start time: {str(e)}")
