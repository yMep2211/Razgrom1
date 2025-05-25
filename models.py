
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, Computed
from sqlalchemy.orm import declarative_base, relationship
from db import engine

Base = declarative_base()

class Категория(Base):
    __tablename__ = 'категория'
    __table_args__ = {'schema': 'prodjectX'}
    
    id = Column(Integer, primary_key=True)
    название = Column(String(100), nullable=False)
    
    платежи = relationship("Платеж", back_populates="категория")

class Пользователь(Base):
    __tablename__ = 'пользователь'
    __table_args__ = {'schema': 'prodjectX'}
    
    id = Column(Integer, primary_key=True)
    фамилия = Column(String(50), nullable=False)
    имя = Column(String(50), nullable=False)
    отчество = Column(String(50))
    логин = Column(String(50), nullable=False, unique=True)
    пароль = Column(String(100), nullable=False)
    пин_код = Column(String(10))
    
    платежи = relationship("ПлатежиПользователей", back_populates="пользователь")

class Платеж(Base):
    __tablename__ = 'платеж'
    __table_args__ = {'schema': 'prodjectX'}
    
    id = Column(Integer, primary_key=True)
    дата = Column(Date, nullable=False)
    наименование_платежа = Column(String(100), nullable=False)
    количество = Column(Numeric(10, 2), default=1)
    цена = Column(Numeric(10, 2), nullable=False)
    стоимость = Column(Numeric(10, 2), Computed("количество * цена"), server_default=None) 
    
    id_категории = Column(Integer, ForeignKey('prodjectX.категория.id'))
    категория = relationship("Категория", back_populates="платежи")
    
    пользователи = relationship("ПлатежиПользователей", back_populates="платеж")

class ПлатежиПользователей(Base):
    __tablename__ = 'платежи_пользователей'
    __table_args__ = {'schema': 'prodjectX'}
    
    id = Column(Integer, primary_key=True)
    id_пользователя = Column(Integer, ForeignKey('prodjectX.пользователь.id'))
    id_платежа = Column(Integer, ForeignKey('prodjectX.платеж.id'))
    
    пользователь = relationship("Пользователь", back_populates="платежи")
    платеж = relationship("Платеж", back_populates="пользователи")


Base.metadata.create_all(engine)