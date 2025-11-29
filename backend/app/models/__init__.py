# pydantic models and shared types
from pydantic import BaseModel
from typing import Optional

class Health(BaseModel):
    status: str

# Add pydantic models for API requests/responses here
