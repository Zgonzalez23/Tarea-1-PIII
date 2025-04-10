from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import Depends

from Base import SessionLocal, engine, Base
from modulos import Personaje, Mision
from create import PersonajeCreate, MisionCreate

app = FastAPI()

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependency para crear sesión de DB por request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear personaje
@app.post("/personajes")
def crear_personaje(personaje: PersonajeCreate, db: Session = Depends(get_db)):
    nuevo = Personaje(nombre=personaje.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"mensaje": "Personaje creado", "id": nuevo.id}

# Crear misión
@app.post("/misiones")
def crear_mision(mision: MisionCreate, db: Session = Depends(get_db)):
    try:
        nueva = Mision(descripcion=mision.descripcion, xp=mision.xp)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)
        return {"mensaje": "Misión creada", "id": nueva.id}
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

# Aceptar misión
@app.post("/personajes/{personaje_id}/misiones/{mision_id}")
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.get(Personaje, personaje_id)
    mision = db.get(Mision, mision_id)
    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrado")
    if mision.personaje_id is not None:
        raise HTTPException(status_code=400, detail="La misión ya está asignada")

    mision.personaje = personaje
    mision.orden = len(personaje.misiones)
    db.commit()
    return {"mensaje": "Misión asignada"}

# Completar misión específica
@app.post("/personajes/{personaje_id}/completar/{mision_id}")
def completar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.get(Personaje, personaje_id)
    mision = db.get(Mision, mision_id)

    if not personaje or not mision:
        raise HTTPException(status_code=404, detail="Personaje o misión no encontrado")
    if mision.personaje_id != personaje.id:
        raise HTTPException(status_code=400, detail="La misión no pertenece a este personaje")

    xp_ganado = mision.xp
    db.delete(mision)
    personaje.xp += xp_ganado
    db.commit()
    return {
        "mensaje": "Misión completada",
        "xp_ganado": xp_ganado,
        "xp_total": personaje.xp
    }

# Listar misiones del personaje
@app.get("/personajes/{personaje_id}/misiones")
def listar_misiones(personaje_id: int, db: Session = Depends(get_db)):
    personaje = db.get(Personaje, personaje_id)
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
