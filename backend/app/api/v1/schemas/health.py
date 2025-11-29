from pydantic import BaseModel
from ._base import CamelModel

class HealthResponse(CamelModel):
    status: str
