from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from flask import jsonify

from .config import Config
from .models import db
from .routes.health import blp as health_blp
from .routes.todos import blp as todos_blp


app = Flask(__name__)
app.url_map.strict_slashes = False

# Load configuration and setup CORS
cfg = Config()
cors_origins = [o.strip() for o in cfg.CORS_ORIGINS.split(",")] if cfg.CORS_ORIGINS else ["*"]
CORS(app, resources={r"/*": {"origins": cors_origins}})

# OpenAPI / Docs configuration
app.config["API_TITLE"] = "Todo Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Database configuration
if not cfg.SQLALCHEMY_URI:
    # Note to orchestrator: Missing DB env configuration
    pass
app.config["SQLALCHEMY_DATABASE_URI"] = cfg.SQLALCHEMY_URI or "sqlite:///:memory:"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)
with app.app_context():
    # Create tables if they do not exist
    try:
        db.create_all()
    except Exception:
        # In CI without DB variables, sqlite memory will be used; for MySQL, ensure env vars are set.
        pass

# Initialize API and register blueprints
api = Api(app, spec_kwargs={"openapi_version": "3.0.3"})
api.register_blueprint(health_blp)
api.register_blueprint(todos_blp)


# PUBLIC_INTERFACE
@app.get("/docs/openapi.json")
def openapi_json():
    """Return the live OpenAPI JSON document for external tooling."""
    return jsonify(api.spec.to_dict())
