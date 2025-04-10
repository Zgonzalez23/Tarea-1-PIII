from pydantic import BaseModel

class PersonajeCreate(BaseModel):
    nombre: str

class MisionCreate(BaseModel):
    descripcion: str
    xp: int = 10
