import sys
from datetime import date, datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableView, QPushButton, QStackedWidget, QLabel, QLineEdit,
    QSpinBox, QMessageBox, QHeaderView, QDialog, QFormLayout, 
    QDateEdit, QDialogButtonBox, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from db import SessionLocal
from table_models import GuestTableModel, RoomTableModel, ServiceTableModel, BookingTableModel
from models import Гость, ТипНомера, Номер, Бронирование, ГостьБронирования, Услуга, УслугаБронирования
from PyQt6.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from sqlalchemy import func, extract, and_
from sqlalchemy.sql import label

class EditGuestDialog(QDialog):
    def __init__(self, guest, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование гостя")
        self.setGeometry(100, 100, 700, 100)
        self.guest = guest
        self.session = session
        
        layout = QVBoxLayout(self)
        
        # Заголовок с логотипом и названием
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = QPixmap("C:/Users/User/Desktop/PZ/pzxz/logo.png")  # Укажите правильный путь к файлу
        scaled_pixmap = pixmap.scaled(100, 100)
        logo_label.setPixmap(scaled_pixmap)
        
        title_label = QLabel("BobirHotel")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        
        # Форма с полями
        form_layout = QFormLayout()
        
        self.last_name_edit = QLineEdit(guest.Фамилия)
        self.first_name_edit = QLineEdit(guest.Имя)
        self.middle_name_edit = QLineEdit(guest.Отчество or "")
        
        # Преобразуем дату рождения в QDate
        birth_date = guest.Дата_рождения
        qdate = QDate(birth_date.year, birth_date.month, birth_date.day)
        self.birth_date_edit = QDateEdit(qdate)
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat("dd.MM.yyyy")
        
        self.passport_series_edit = QLineEdit(guest.Паспорт_серия or "")
        self.passport_number_edit = QLineEdit(guest.Паспорт_номер or "")
        
        # Дата выдачи паспорта (может быть None)
        passport_issued = guest.Паспорт_выдан
        if passport_issued:
            qdate_issued = QDate(passport_issued.year, passport_issued.month, passport_issued.day)
            self.passport_issued_edit = QDateEdit(qdate_issued)
        else:
            self.passport_issued_edit = QDateEdit()
        self.passport_issued_edit.setCalendarPopup(True)
        self.passport_issued_edit.setDisplayFormat("dd.MM.yyyy")
        self.passport_issued_edit.setSpecialValueText("Не указана")
        
        self.address_edit = QLineEdit(guest.Адрес or "")
        self.phone_edit = QLineEdit(guest.Телефон)
        
        # Добавляем поля в форму
        form_layout.addRow("Фамилия:", self.last_name_edit)
        form_layout.addRow("Имя:", self.first_name_edit)
        form_layout.addRow("Отчество:", self.middle_name_edit)
        form_layout.addRow("Дата рождения:", self.birth_date_edit)
        form_layout.addRow("Серия паспорта:", self.passport_series_edit)
        form_layout.addRow("Номер паспорта:", self.passport_number_edit)
        form_layout.addRow("Паспорт выдан:", self.passport_issued_edit)
        form_layout.addRow("Адрес:", self.address_edit)
        form_layout.addRow("Телефон:", self.phone_edit)
        
        # Кнопки OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
    
    def accept(self):
        # Валидация обязательных полей
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Фамилия не может быть пустой")
            return
            
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым")
            return
            
        if not self.phone_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Телефон не может быть пустым")
            return
            
        try:
            # Обновляем данные гостя
            self.guest.Фамилия = self.last_name_edit.text().strip()
            self.guest.Имя = self.first_name_edit.text().strip()
            self.guest.Отчество = self.middle_name_edit.text().strip() or None
            self.guest.Дата_рождения = self.birth_date_edit.date().toPyDate()
            self.guest.Паспорт_серия = self.passport_series_edit.text().strip() or None
            self.guest.Паспорт_номер = self.passport_number_edit.text().strip() or None
            self.guest.Паспорт_выдан = self.passport_issued_edit.date().toPyDate() if not self.passport_issued_edit.date().isNull() else None
            self.guest.Адрес = self.address_edit.text().strip() or None
            self.guest.Телефон = self.phone_edit.text().strip()
            
            # Сохраняем в БД
            self.session.commit()
            super().accept()
            
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {str(e)}")

class AddGuestDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BobirHotel - Добавление гостя")
        self.setGeometry(100, 100, 700, 100)
        self.session = session
        
        layout = QVBoxLayout(self)
        
        # Заголовок с логотипом и названием
        """ 
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = QPixmap("C:/Users/User/Desktop/PZ/pzxz/logo.png")  # Укажите правильный путь к файлу
        scaled_pixmap = pixmap.scaled(100, 100)
        logo_label.setPixmap(scaled_pixmap)
        
        title_label = QLabel("BobirHotel")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch() 
        
        
        layout.addLayout(header_layout)
        """
        
        # Форма с полями
        form_layout = QFormLayout()
        
        self.last_name_edit = QLineEdit()
        self.first_name_edit = QLineEdit()
        self.middle_name_edit = QLineEdit()
        
        self.birth_date_edit = QDateEdit(QDate.currentDate())
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat("dd.MM.yyyy")
        
        self.passport_series_edit = QLineEdit()
        self.passport_number_edit = QLineEdit()
        
        self.passport_issued_edit = QDateEdit()
        self.passport_issued_edit.setCalendarPopup(True)
        self.passport_issued_edit.setDisplayFormat("dd.MM.yyyy")
        self.passport_issued_edit.setSpecialValueText("Не указана")
        
        self.address_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        
        # Добавляем поля в форму
        form_layout.addRow("Фамилия*:", self.last_name_edit)
        form_layout.addRow("Имя*:", self.first_name_edit)
        form_layout.addRow("Отчество:", self.middle_name_edit)
        form_layout.addRow("Дата рождения*:", self.birth_date_edit)
        form_layout.addRow("Серия паспорта:", self.passport_series_edit)
        form_layout.addRow("Номер паспорта:", self.passport_number_edit)
        form_layout.addRow("Паспорт выдан:", self.passport_issued_edit)
        form_layout.addRow("Адрес:", self.address_edit)
        form_layout.addRow("Телефон*:", self.phone_edit)
        
        # Кнопки OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                    QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        

    
    def accept(self):
        # Валидация обязательных полей
        if not self.last_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Фамилия не может быть пустой")
            return
            
        if not self.first_name_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым")
            return
            
        if not self.phone_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Телефон не может быть пустым")
            return
        
        # Проверка возраста (минимум 18 лет)
        birth_date = self.birth_date_edit.date().toPyDate()
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 18:
            QMessageBox.warning(
                self, 
                "Ошибка", 
                "Невозможно добавить гостя младше 18 лет!\n"
                f"Указанный возраст: {age} лет"
            )
            return
            
        try:
            # Создаем нового гостя
            new_guest = Гость(
                Фамилия=self.last_name_edit.text().strip(),
                Имя=self.first_name_edit.text().strip(),
                Отчество=self.middle_name_edit.text().strip() or None,
                Дата_рождения=birth_date,
                Паспорт_серия=self.passport_series_edit.text().strip() or None,
                Паспорт_номер=self.passport_number_edit.text().strip() or None,
                Паспорт_выдан=self.passport_issued_edit.date().toPyDate() if not self.passport_issued_edit.date().isNull() else None,
                Адрес=self.address_edit.text().strip() or None,
                Телефон=self.phone_edit.text().strip()
            )
            
            # Добавляем в БД
            self.session.add(new_guest)
            self.session.commit()
            super().accept()
            
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить гостя: {str(e)}")

class AddRoomDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Добавить номер")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Заголовок с логотипом и названием
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = QPixmap("C:/Users/User/Desktop/PZ/pzxz/logo.png")  # Укажите правильный путь к файлу
        scaled_pixmap = pixmap.scaled(100, 100)
        logo_label.setPixmap(scaled_pixmap)
        
        title_label = QLabel("BobirHotel")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Выпадающий список для типа номера
        self.type_combo = QComboBox()
        room_types = session.query(ТипНомера).all()
        for rt in room_types:
            self.type_combo.addItem(f"{rt.Название} ({rt.Цена_сутки}₽/сут)", rt.ID)
        
        # Поля ввода
        self.room_number_edit = QLineEdit()
        self.room_number_edit.setPlaceholderText("Например: 101A")
        
        # Форма
        form = QFormLayout()
        form.addRow("Тип номера*:", self.type_combo)
        form.addRow("Номер комнаты*:", self.room_number_edit)
        
        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.validate_and_save)
        btn_box.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(btn_box)
    
    def validate_and_save(self):
        if not self.room_number_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите номер комнаты")
            return
            
        try:
            new_room = Номер(
                Тип_ID=self.type_combo.currentData(),
                Номер_комнаты=self.room_number_edit.text().strip(),
                Статус="свободен"
            )
            self.session.add(new_room)
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")

class AddBookingDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Добавить бронирование")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Заголовок с логотипом и названием
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        pixmap = QPixmap("C:/Users/User/Desktop/PZ/pzxz/logo.png")  # Укажите правильный путь к файлу
        scaled_pixmap = pixmap.scaled(100, 100)
        logo_label.setPixmap(scaled_pixmap)
        
        title_label = QLabel("BobirHotel")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Выпадающие списки
        self.guest_combo = QComboBox()
        guests = session.query(Гость).order_by(Гость.Фамилия).all()
        for guest in guests:
            self.guest_combo.addItem(f"{guest.Фамилия} {guest.Имя}", guest.ID)
        
        self.room_combo = QComboBox()
        rooms = session.query(Номер).filter(Номер.Статус == "свободен").all()
        for room in rooms:
            self.room_combo.addItem(f"№{room.Номер_комнаты} ({room.тип.Название})", room.ID)
        
        # Поля дат
        self.date_in = QDateEdit(QDate.currentDate())
        self.date_in.setCalendarPopup(True)
        self.date_out = QDateEdit(QDate.currentDate().addDays(1))
        self.date_out.setCalendarPopup(True)
        
        # Форма
        form = QFormLayout()
        form.addRow("Гость*:", self.guest_combo)
        form.addRow("Номер*:", self.room_combo)
        form.addRow("Дата заезда*:", self.date_in)
        form.addRow("Дата выезда*:", self.date_out)
        
        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                  QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.validate_and_save)
        btn_box.rejected.connect(self.reject)
        
        layout.addLayout(form)
        layout.addWidget(btn_box)
    
    def validate_and_save(self):
        if self.date_in.date() >= self.date_out.date():
            QMessageBox.warning(self, "Ошибка", "Дата выезда должна быть позже даты заезда")
            return
            
        try:
            # Создаем бронирование
            booking = Бронирование(
                Гость_ID=self.guest_combo.currentData(),
                Номер_ID=self.room_combo.currentData(),
                Дата_заезда=self.date_in.date().toPyDate(),
                Дата_выезда=self.date_out.date().toPyDate(),
                Статус_оплаты="не оплачено"
            )
            
            # Меняем статус номера
            room = self.session.query(Номер).get(self.room_combo.currentData())
            room.Статус = "забронирован"
            
            self.session.add(booking)
            self.session.commit()
            self.accept()
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")

        
class StatisticsDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Статистика")
        self.setGeometry(100, 100, 1000, 700)
        
        # Создаем основную вкладку (теперь только одна)
        self.tab_finance = QWidget()
        self.setup_finance_tab()
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_finance)
    
    def setup_finance_tab(self):
        layout = QVBoxLayout(self.tab_finance)
        
        # Кнопки для переключения диаграмм
        btn_layout = QHBoxLayout()
        
        self.btn_fin_hist = QPushButton("Гистограмма")
        self.btn_fin_hist.clicked.connect(lambda: self.show_finance_diagram(0))
        
        self.btn_fin_line = QPushButton("График")
        self.btn_fin_line.clicked.connect(lambda: self.show_finance_diagram(1))
        
        self.btn_fin_pie = QPushButton("Круговая")
        self.btn_fin_pie.clicked.connect(lambda: self.show_finance_diagram(2))
        
        btn_layout.addWidget(self.btn_fin_hist)
        btn_layout.addWidget(self.btn_fin_line)
        btn_layout.addWidget(self.btn_fin_pie)
        
        # Область для диаграммы
        self.figure_finance = Figure(figsize=(10, 6), dpi=100)
        self.canvas_finance = FigureCanvas(self.figure_finance)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.canvas_finance)
        
        # Загружаем данные и показываем первую диаграмму
        self.load_finance_data()
        self.show_finance_diagram(0)
    
    def load_finance_data(self):
        """Загрузка финансовых данных из БД"""
        try:
            # Доход по месяцам
            monthly_income = self.session.query(
                label('month', func.date_format(Бронирование.Дата_заезда, '%Y-%m')),
                label('income', func.coalesce(func.sum(
                    ТипНомера.Цена_сутки * 
                    func.datediff(Бронирование.Дата_выезда, Бронирование.Дата_заезда)
                ), 0))
            ).join(Номер, Бронирование.Номер_ID == Номер.ID
            ).join(ТипНомера, Номер.Тип_ID == ТипНомера.ID
            ).group_by('month').order_by('month').all()
            
            # Доход по типам номеров
            income_by_type = self.session.query(
                ТипНомера.Название,
                label('income', func.coalesce(func.sum(
                    ТипНомера.Цена_сутки * 
                    func.datediff(Бронирование.Дата_выезда, Бронирование.Дата_заезда)
                ), 0))
            ).join(Номер, Номер.Тип_ID == ТипНомера.ID
            ).join(Бронирование, Бронирование.Номер_ID == Номер.ID
            ).group_by(ТипНомера.ID).all()
            
            self.finance_data = {
                'Месяцы': [stat[0] for stat in monthly_income],
                'Доход': [float(stat[1]) for stat in monthly_income],
                'Типы номеров': [stat[0] for stat in income_by_type],
                'Доход по типам': [float(stat[1]) for stat in income_by_type]
            }
            
        except Exception as e:
            print(f"Ошибка загрузки финансовых данных: {e}")
            self.finance_data = {
                'Месяцы': ['2023-01', '2023-02'], 
                'Доход': [0, 0],
                'Типы номеров': ['Стандарт', 'Люкс'], 
                'Доход по типам': [0, 0]
            }
    
    def show_finance_diagram(self, diagram_type):
        self.figure_finance.clear()
        ax = self.figure_finance.add_subplot(111)
        
        if not self.finance_data['Месяцы'] or sum(self.finance_data['Доход']) == 0:
            ax.text(0.5, 0.5, 'Нет данных для отображения', 
                    ha='center', va='center', fontsize=12)
        else:
            if diagram_type == 0:  # Гистограмма дохода по месяцам
                ax.bar(self.finance_data['Месяцы'], self.finance_data['Доход'])
                ax.set_title('Доход по месяцам')
                ax.set_xlabel('Месяц')
                ax.set_ylabel('Доход, руб.')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(axis='y')
                
            elif diagram_type == 1:  # График динамики дохода
                ax.plot(self.finance_data['Месяцы'], self.finance_data['Доход'], 
                    marker='o', linestyle='-', color='g')
                ax.set_title('Динамика дохода')
                ax.set_xlabel('Месяц')
                ax.set_ylabel('Доход, руб.')
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True)
                
            elif diagram_type == 2:  # Круговая диаграмма дохода по типам номеров
                ax.pie(
                    self.finance_data['Доход по типам'],
                    labels=self.finance_data['Типы номеров'],
                    autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
                    startangle=90
                )
                ax.set_title('Распределение дохода по типам номеров')
        
        self.figure_finance.tight_layout()
        self.canvas_finance.draw()

class HotelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Гостиничная система")
        self.setGeometry(100, 100, 1200, 700)
        self.session = SessionLocal()
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Боковая панель
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Логотип и название в сайдбаре
        logo_label = QLabel()
        pixmap = QPixmap("C:/Users/User/Desktop/PZ/pzxz/logo.png")  # Укажите правильный путь к файлу
        scaled_pixmap = pixmap.scaled(100, 100)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("BobirHotel")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sidebar_layout.addWidget(logo_label)
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addSpacing(20)
        
        # Кнопки меню
        self.btn_guests = QPushButton("Клиенты")
        self.btn_rooms = QPushButton("Номера")
        self.btn_services = QPushButton("Услуги")
        self.btn_bookings = QPushButton("Бронирования")
        self.btn_statistic = QPushButton("Статистика")
        
        self.btn_guests.clicked.connect(self.show_guests)
        self.btn_rooms.clicked.connect(self.show_rooms)
        self.btn_services.clicked.connect(self.show_services)
        self.btn_bookings.clicked.connect(self.show_bookings)
        self.btn_statistic.clicked.connect(self.show_statistics)
        
        sidebar_layout.addWidget(self.btn_guests)
        sidebar_layout.addWidget(self.btn_rooms)
        sidebar_layout.addWidget(self.btn_services)
        sidebar_layout.addWidget(self.btn_bookings)
        sidebar_layout.addWidget(self.btn_statistic)
        sidebar_layout.addStretch()
        
        # Область контента
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # Виджет для переключения
        self.stacked_widget = QStackedWidget()
        
        # Создаем вкладки
        self.create_guests_tab()
        self.create_rooms_tab()
        self.create_services_tab()
        self.create_bookings_tab()
        
        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
    
    def create_guests_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Поиск и фильтрация по возрасту
        search_filter_layout = QHBoxLayout()
        
        self.search_guest = QLineEdit()
        self.search_guest.setPlaceholderText("Поиск по фамилии...")
        self.search_guest.textChanged.connect(self.filter_guests)
        
        self.age_from = QSpinBox()
        self.age_from.setRange(0, 120)
        self.age_from.setValue(18)
        self.age_from.valueChanged.connect(self.filter_guests)
        
        self.age_to = QSpinBox()
        self.age_to.setRange(0, 180)
        self.age_to.setValue(100)
        self.age_to.valueChanged.connect(self.filter_guests)
        
        search_filter_layout.addWidget(QLabel("Поиск:"))
        search_filter_layout.addWidget(self.search_guest)
        search_filter_layout.addWidget(QLabel("Возраст от:"))
        search_filter_layout.addWidget(self.age_from)
        search_filter_layout.addWidget(QLabel("до:"))
        search_filter_layout.addWidget(self.age_to)
        
        # Таблица гостей
        self.guests_table = QTableView()
        self.setup_table(self.guests_table)
        
        # Кнопки изменения и добавления
        buttons_layout = QHBoxLayout()
        
        self.btn_add_guest = QPushButton("Добавить")
        self.btn_add_guest.clicked.connect(self.add_guest)
        buttons_layout.addWidget(self.btn_add_guest)
        
        self.btn_edit_guest = QPushButton("Изменить")
        self.btn_edit_guest.clicked.connect(self.edit_guest)
        buttons_layout.addWidget(self.btn_edit_guest)
        
        buttons_layout.addStretch()
        
        layout.addLayout(search_filter_layout)
        layout.addWidget(self.guests_table)
        layout.addLayout(buttons_layout)
        
        self.stacked_widget.addWidget(tab)
    
    def create_rooms_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Поиск (оставляем сверху)
        search_layout = QHBoxLayout()
        self.search_room = QLineEdit()
        self.search_room.setPlaceholderText("Поиск по номеру...")
        self.search_room.textChanged.connect(self.filter_rooms)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_room)
        layout.addLayout(search_layout)
        
        # Таблица
        self.rooms_table = QTableView()
        self.rooms_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setup_table(self.rooms_table)
        layout.addWidget(self.rooms_table)
        
        # Кнопка добавления (ПЕРЕМЕЩАЕМ ВНИЗ)
        buttons_layout = QHBoxLayout()
        self.btn_add_room = QPushButton("Добавить")
        self.btn_add_room.clicked.connect(self.add_room)
        buttons_layout.addWidget(self.btn_add_room)  # Можно добавить другие кнопки справа
        buttons_layout.addStretch()  # Выравнивание по левому краю
        
        layout.addLayout(buttons_layout)
        self.stacked_widget.addWidget(tab)

    def add_room(self):
        dialog = AddRoomDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.room_model.source_rooms = self.session.query(Номер).join(ТипНомера).all()
            self.room_model.layoutChanged.emit()
            QMessageBox.information(self, "Успех", "Номер успешно добавлен")
    
    def create_services_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Поиск для услуг
        search_layout = QHBoxLayout()
        self.search_service = QLineEdit()
        self.search_service.setPlaceholderText("Поиск по названию...")
        self.search_service.textChanged.connect(self.filter_services)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_service)
        
        # Таблица услуг
        self.services_table = QTableView()
        self.setup_table(self.services_table)
        
        layout.addLayout(search_layout)
        layout.addWidget(self.services_table)
        
        self.stacked_widget.addWidget(tab)
    
    def create_bookings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Поиск (сверху)
        search_layout = QHBoxLayout()
        self.search_booking = QLineEdit()
        self.search_booking.setPlaceholderText("Поиск по фамилии...")
        self.search_booking.textChanged.connect(self.filter_bookings)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_booking)
        layout.addLayout(search_layout)
        
        # Таблица
        self.bookings_table = QTableView()
        self.bookings_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setup_table(self.bookings_table)
        layout.addWidget(self.bookings_table)
        
        # Кнопка добавления (ПЕРЕМЕЩАЕМ ВНИЗ)
        buttons_layout = QHBoxLayout()
        self.btn_add_booking = QPushButton("Добавить ")
        self.btn_add_booking.clicked.connect(self.add_booking)
        buttons_layout.addWidget(self.btn_add_booking)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        self.stacked_widget.addWidget(tab)

    def add_booking(self):
        dialog = AddBookingDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.booking_model.source_bookings = self.session.query(Бронирование).all()
            self.booking_model.layoutChanged.emit()
            QMessageBox.information(self, "Успех", "Бронирование успешно добавлено")
    
    def setup_table(self, table):
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)
    
    def load_data(self):
        # Загружаем модели
        self.guest_model = GuestTableModel(self.session)
        self.room_model = RoomTableModel(self.session)
        self.service_model = ServiceTableModel(self.session)
        self.booking_model = BookingTableModel(self.session)
        
        # Устанавливаем модели
        self.guests_table.setModel(self.guest_model)
        self.rooms_table.setModel(self.room_model)
        self.services_table.setModel(self.service_model)
        self.bookings_table.setModel(self.booking_model)
    
        # Убираем вызовы filter_*() здесь, они будут вызываться при показе вкладок
    
    def calculate_age(self, birth_date):
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def filter_guests(self):
        search_text = self.search_guest.text().lower()
        age_from = self.age_from.value()
        age_to = self.age_to.value()
        
        # Обновляем данные только если source_guests пуст или None
        if not hasattr(self.guest_model, 'source_guests') or not self.guest_model.source_guests:
            self.guest_model.source_guests = self.session.query(Гость).all()
        
        filtered = []
        for guest in self.guest_model.source_guests:
            age = self.calculate_age(guest.Дата_рождения)
            if (search_text in guest.Фамилия.lower() and 
                age_from <= age <= age_to):
                filtered.append(guest)
        
        self.guest_model.guests = filtered
        # Используем dataChanged для более эффективного обновления
        self.guest_model.layoutAboutToBeChanged.emit()
        self.guest_model.layoutChanged.emit()
            
        self.guest_model.guests = filtered
        self.guest_model.layoutChanged.emit()
    
    def filter_rooms(self):
        if not hasattr(self, 'search_room') or not self.search_room:
            return
        
        search_text = self.search_room.text().lower()
    
        filtered = []
        for room in self.room_model.source_rooms:
            if search_text in room.Номер_комнаты.lower():
                filtered.append(room)
    
        self.room_model.rooms = filtered
        self.room_model.layoutChanged.emit()
    
    def filter_services(self):
        search_text = self.search_service.text().lower()
        
        filtered = []
        for service in self.service_model.source_services:
            if search_text in service.Название.lower():
                filtered.append(service)
        
        self.service_model.services = filtered
        self.service_model.layoutChanged.emit()
    
    def filter_bookings(self):
        search_text = self.search_booking.text().lower()
        
        filtered = []
        for booking in self.booking_model.source_bookings:
            if search_text in booking.гость.Фамилия.lower():
                filtered.append(booking)
        
        self.booking_model.bookings = filtered
        self.booking_model.layoutChanged.emit()
    
    def edit_guest(self):
        selected = self.guests_table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите гостя для редактирования")
            return
        
        selected_row = selected[0].row()
        guest = self.guest_model.guests[selected_row]
        
        dialog = EditGuestDialog(guest, self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.guest_model.load_data()  # Обновляем данные после редактирования
            self.filter_guests()
            QMessageBox.information(self, "Успех", "Данные гостя успешно обновлены")
            
    def add_guest(self):  # Важно: именно add_guest, а не add_room
        dialog = AddGuestDialog(self.session, self)  # Должен быть AddGuestDialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.guest_model.load_data()
            self.filter_guests()
            QMessageBox.information(self, "Успех", "Гость успешно добавлен")

    
    def show_rooms(self):
        self.stacked_widget.setCurrentIndex(1)
        self.filter_rooms()  # Теперь фильтрация вызывается здесь

    def show_guests(self):
        self.stacked_widget.setCurrentIndex(0)
        self.filter_guests()

    def show_services(self):
        self.stacked_widget.setCurrentIndex(2)
        self.filter_services()

    def show_bookings(self):
        self.stacked_widget.setCurrentIndex(3)
        self.filter_bookings()
    
    def closeEvent(self, event):
        self.session.close()
        event.accept()
        
    def show_statistics(self):
    # Проверяем, есть ли данные в БД
        has_data = self.session.query(Бронирование).first() is not None
        
        if not has_data:
            QMessageBox.information(self, "Нет данных", 
                                "В базе данных нет информации о бронированиях для построения статистики.")
            return
        
        dialog = StatisticsDialog(self.session, self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HotelApp()
    window.show()
    sys.exit(app.exec())