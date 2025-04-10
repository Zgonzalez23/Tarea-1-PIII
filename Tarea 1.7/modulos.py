from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import Base

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
    xp = Column(Integer, default=10)
    personaje_id = Column(Integer, ForeignKey("personajes.id"))
    orden = Column(Integer)
    personaje = relationship("Personaje", back_populates="misiones")
