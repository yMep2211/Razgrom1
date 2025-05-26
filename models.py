from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class Гость(Base):
    __tablename__ = 'Гость'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Фамилия = Column(String(100), nullable=False)
    Имя = Column(String(100), nullable=False)
    Отчество = Column(String(100))
    Дата_рождения = Column(Date, nullable=False)
    Паспорт_серия = Column(String(10))
    Паспорт_номер = Column(String(20))
    Паспорт_выдан = Column(Date)
    Адрес = Column(String(500))
    Телефон = Column(String(20), nullable=False)
    
    бронирования = relationship("Бронирование", back_populates="гость")
    сопутствующие_гости = relationship("ГостьБронирования", back_populates="гость")

class ТипНомера(Base):
    __tablename__ = 'ТипНомера'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Название = Column(String(200), nullable=False, unique=True)
    Описание = Column(String(1000))
    Цена_сутки = Column(Float, nullable=False)
    
    номера = relationship("Номер", back_populates="тип")

class Номер(Base):
    __tablename__ = 'Номер'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Тип_ID = Column(Integer, ForeignKey('ТипНомера.ID'), nullable=False)
    Номер_комнаты = Column(String(10), nullable=False, unique=True)
    Статус = Column(String(50), server_default='свободен')
    
    тип = relationship("ТипНомера", back_populates="номера")
    бронирования = relationship("Бронирование", back_populates="номер")

class Услуга(Base):
    __tablename__ = 'Услуга'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Название = Column(String(200), nullable=False, unique=True)
    Описание = Column(String(1000))
    Цена = Column(Float)

class Бронирование(Base):
    __tablename__ = 'Бронирование'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Гость_ID = Column(Integer, ForeignKey('Гость.ID'), nullable=False)
    Номер_ID = Column(Integer, ForeignKey('Номер.ID'), nullable=False)
    Дата_заезда = Column(Date, nullable=False)
    Дата_выезда = Column(Date, nullable=False)
    Статус_оплаты = Column(String(50), server_default='не оплачено')
    
    гость = relationship("Гость", back_populates="бронирования")
    номер = relationship("Номер", back_populates="бронирования")
    услуги = relationship("УслугаБронирования", back_populates="бронирование")
    дополнительные_гости = relationship("ГостьБронирования", back_populates="бронирование")

class ГостьБронирования(Base):
    __tablename__ = 'ГостьБронирования'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Бронирование_ID = Column(Integer, ForeignKey('Бронирование.ID'), nullable=False)
    Гость_ID = Column(Integer, ForeignKey('Гость.ID'), nullable=False)
    
    бронирование = relationship("Бронирование", back_populates="дополнительные_гости")
    гость = relationship("Гость", back_populates="сопутствующие_гости")

class УслугаБронирования(Base):
    __tablename__ = 'УслугаБронирования'
    
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Бронирование_ID = Column(Integer, ForeignKey('Бронирование.ID'), nullable=False)
    Услуга_ID = Column(Integer, ForeignKey('Услуга.ID'), nullable=False)
    Количество = Column(Integer, server_default='1')
    
    бронирование = relationship("Бронирование", back_populates="услуги")
    услуга = relationship("Услуга")