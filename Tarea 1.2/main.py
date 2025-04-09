from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
engine = create_engine('sqlite:///rpg.db')
Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()

# --- MODELOS ORM ---
class Personaje(Base):
    __tablename__ = "personajes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    xp = Column(Integer, default=0)
    misiones = relationship("Mision", back_populates="personaje", order_by="Mision.orden")

class Mision(Base):
    __tablename__ = "misiones"
    id = Column(Integer, primary_key=True)
    descripcion = Column(String, nullable=False)
    xp = Column(Integer, default=10)  # XP por defecto si no se define
    personaje_id = Column(Integer, ForeignKey("personajes.id"))
    orden = Column(Integer)
    personaje = relationship("Personaje", back_populates="misiones")

Base.metadata.create_all(engine)

# --- ESQUEMAS Pydantic ---
class PersonajeCreate(BaseModel):
    nombre: str

class MisionCreate(BaseModel):
    descripcion: str
    xp: int = 10  # Valor por defecto

# --- ENDPOINTS ---

# Crear personaje
@app.post("/personajes")
def crear_personaje(personaje: PersonajeCreate):
    nuevo = Personaje(nombre=personaje.nombre)
    session.add(nuevo)
    session.commit()
    return {"mensaje": "Personaje creado", "id": nuevo.id}

# Crear misión
@app.post("/misiones")
def crear_mision(mision: MisionCreate):
    nueva = Mision(descripcion=mision.descripcion, xp=mision.xp)
    session.add(nueva)
    session.commit()
    return {"mensaje": "Misión creada", "id": nueva.id}

# Aceptar misión (encolar)
@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int):
    personaje = session.get(Personaje, personaje_id)
    mision = session.get(Mision, mision_id)
    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrado")
    if mision.personaje_id is not None:
        raise HTTPException(status_code=400, detail="La misión ya está asignada")

    mision.personaje = personaje
    mision.orden = len(personaje.misiones)
    session.commit()
    return {"mensaje": "Misión asignada"}

# Completar misión específica
@app.post("/personajes/{personaje_id}/completar/{mision_id}")
def completar_mision(personaje_id: int, mision_id: int):
    personaje = session.get(Personaje, personaje_id)
    mision = session.get(Mision, mision_id)

    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrado")

    if mision.personaje_id != personaje.id:
        raise HTTPException(status_code=400, detail="La misión no pertenece a este personaje")

    xp_ganado = mision.xp
    session.delete(mision)
    personaje.xp += xp_ganado
    session.commit()
    return {
        "mensaje": "Misión completada",
        "xp_ganado": xp_ganado,
        "xp_total": personaje.xp
    }

# Listar misiones con XP
@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int):
    personaje = session.get(Personaje, personaje_id)
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    return [
        {
            "id": m.id,
            "descripcion": m.descripcion,
            "xp": m.xp,
            "orden": m.orden
        }
        for m in personaje.misiones
    ]
