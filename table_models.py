from PyQt6.QtCore import Qt, QAbstractTableModel
from sqlalchemy.orm import Session
from models import Гость, Номер, Услуга, Бронирование, ТипНомера

class GuestTableModel(QAbstractTableModel):
    def __init__(self, session: Session):
            super().__init__()
            self.session = session
            self.headers = ["ID", "Фамилия", "Имя", "Отчество", "Телефон", "Дата рождения"]
            self.load_data()  # Загружаем данные при инициализации
        
    def load_data(self):
        """Загружает данные из базы и обновляет модель"""
        self.source_guests = self.session.query(Гость).all()
        self.guests = self.source_guests.copy()
        self.layoutChanged.emit()  # Уведомляем view об изменении данных
    
    def rowCount(self, parent=None):
        return len(self.guests)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            guest = self.guests[index.row()]
            return [
                guest.ID,
                guest.Фамилия,
                guest.Имя,
                guest.Отчество or "",
                guest.Телефон,
                guest.Дата_рождения.strftime("%d.%m.%Y")
            ][index.column()]
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class RoomTableModel(QAbstractTableModel):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.headers = ["ID", "Номер", "Тип", "Статус", "Цена"]
        self.source_rooms = session.query(Номер).join(ТипНомера).all()
        self.rooms = self.source_rooms.copy()
    
    def load_data(self):
        self.source_rooms = self.session.query(Номер).join(ТипНомера).all()
        self.rooms = self.source_rooms.copy()
        self.layoutChanged.emit()
    
    def rowCount(self, parent=None):
        return len(self.rooms)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            room = self.rooms[index.row()]
            return [
                room.ID,
                room.Номер_комнаты,
                room.тип.Название,
                room.Статус,
                f"{room.тип.Цена_сутки:.2f} ₽"
            ][index.column()]
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class ServiceTableModel(QAbstractTableModel):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.headers = ["ID", "Название", "Описание", "Цена"]
        self.source_services = session.query(Услуга).all()
        self.services = self.source_services.copy()
    
    def rowCount(self, parent=None):
        return len(self.services)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            service = self.services[index.row()]
            price = f"{service.Цена:.2f} ₽" if service.Цена else "Бесплатно"
            return [
                service.ID,
                service.Название,
                service.Описание or "",
                price
            ][index.column()]
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None

class BookingTableModel(QAbstractTableModel):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.headers = ["ID", "Гость", "Номер", "Заезд", "Выезд", "Статус"]
        self.source_bookings = session.query(Бронирование).join(Гость).join(Номер).all()
        self.bookings = self.source_bookings.copy()
    
    def load_data(self):
        self.source_bookings = self.session.query(Бронирование).join(Гость).join(Номер).all()
        self.bookings = self.source_bookings.copy()
        self.layoutChanged.emit()
    
    def rowCount(self, parent=None):
        return len(self.bookings)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            booking = self.bookings[index.row()]
            return [
                booking.ID,
                f"{booking.гость.Фамилия} {booking.гость.Имя}",
                booking.номер.Номер_комнаты,
                booking.Дата_заезда.strftime("%d.%m.%Y"),
                booking.Дата_выезда.strftime("%d.%m.%Y"),
                booking.Статус_оплаты
            ][index.column()]
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.headers[section]
        return None