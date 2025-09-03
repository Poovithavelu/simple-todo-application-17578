from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance (initialized in app factory)
db = SQLAlchemy()


class Todo(db.Model):
    """
    PUBLIC_INTERFACE
    SQLAlchemy model representing a Todo item.
    """
    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    start_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    def to_dict(self):
        """
        PUBLIC_INTERFACE
        Serialize the Todo model to a plain dict for JSON responses.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
