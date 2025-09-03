import os
from dataclasses import dataclass


@dataclass
class Config:
    """
    PUBLIC_INTERFACE
    Application configuration loaded from environment variables.

    Required environment variables (set by orchestrator in .env):
    - MYSQL_URL: Host or full URL for MySQL server (hostname or IP)
    - MYSQL_USER: Username for DB authentication
    - MYSQL_PASSWORD: Password for DB authentication
    - MYSQL_DB: Database name
    - MYSQL_PORT: Port number (e.g., 3306)
    - CORS_ORIGINS: Comma-separated list of allowed CORS origins; "*" to allow all (default "*")
    """
    MYSQL_URL: str = os.getenv("MYSQL_URL", "")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))

    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def SQLALCHEMY_URI(self) -> str:
        """
        PUBLIC_INTERFACE
        Build a SQLAlchemy-compatible MySQL URI using PyMySQL driver.
        """
        host = self.MYSQL_URL
        user = self.MYSQL_USER
        pwd = self.MYSQL_PASSWORD
        db = self.MYSQL_DB
        port = self.MYSQL_PORT
        if not all([host, user, pwd, db]):
            # Return empty; caller should handle missing configuration gracefully
            return ""
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"
