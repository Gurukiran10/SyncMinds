"""
SQLAlchemy type utilities for cross-database compatibility
"""
from sqlalchemy import String, TypeDecorator, event
from sqlalchemy.dialects.postgresql import UUID
import uuid as uuid_module


class GUID(TypeDecorator):
    """
    Platform-agnostic GUID type that works with SQLite and PostgreSQL.
    Uses UUID in PostgreSQL and VARCHAR(36) in SQLite.
    """
    impl = String(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        
        if isinstance(value, uuid_module.UUID):
            if dialect.name == 'postgresql':
                return value
            return str(value)
        
        # If it's already a string, assume it's valid
        if isinstance(value, str):
            if dialect.name == 'postgresql':
                try:
                    return uuid_module.UUID(value)
                except (ValueError, TypeError):
                    return value
            return value
        
        # Try to convert to UUID
        if dialect.name == 'postgresql':
            try:
                return uuid_module.UUID(str(value))
            except (ValueError, TypeError):
                return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        if isinstance(value, uuid_module.UUID):
            return value
        
        try:
            return uuid_module.UUID(str(value))
        except (ValueError, TypeError, AttributeError):
            return value
