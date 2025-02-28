import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QFrame
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My SQLite App")
        self.setGeometry(100, 100, 1000, 600)  # Szerokość x Wysokość
        self.setStyleSheet(open("style.qss", "r").read())  # Wczytanie stylu

        # Główny widget
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # --- Lewy panel (Nawigacja) ---
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(self.left_panel)

        self.btn_home = QPushButton("Home")
        self.btn_reports = QPushButton("Reports")
        self.btn_account = QPushButton("My Account")

        left_layout.addWidget(self.btn_home)
        left_layout.addWidget(self.btn_reports)
        left_layout.addWidget(self.btn_account)
        left_layout.addStretch()  # Rozciągnięcie przestrzeni

        self.btn_settings = QPushButton("Settings")
        self.btn_help = QPushButton("Help")
        self.btn_about = QPushButton("About")

        left_layout.addWidget(self.btn_settings)
        left_layout.addWidget(self.btn_help)
        left_layout.addWidget(self.btn_about)

        # --- Centralna część (Tabela) ---
        self.center_panel = QWidget()
        center_layout = QVBoxLayout(self.center_panel)

        self.label_title = QLabel("Home Page")
        self.label_title.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.table = QTableWidget(6, 4)  # 6 wierszy, 4 kolumny
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Email", "Phone Number"])
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 200)

        # Dodawanie przykładowych danych
        sample_data = [
            (1, "New User", "user@mail.com", "87654345"),
            (2, "Another User", "new@mail.com", "876543"),
            (3, "Test", "test@mail.com", "345676675"),
            (4, "New Row", "row@mail.com", "5456654523"),
            (5, "New Data", "data@mail.com", "9876534"),
            (6, "Spinn Tv", "spinntv@mail.com", "09876543"),
        ]

        for row, (id, username, email, phone) in enumerate(sample_data):
            self.table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.table.setItem(row, 1, QTableWidgetItem(username))
            self.table.setItem(row, 2, QTableWidgetItem(email))
            self.table.setItem(row, 3, QTableWidgetItem(phone))

        center_layout.addWidget(self.label_title)
        center_layout.addWidget(self.table)

        # --- Prawy panel (Formularz) ---
        self.right_panel = QWidget()
        self.right_panel.setFixedWidth(250)
        right_layout = QVBoxLayout(self.right_panel)

        self.label_add_user = QLabel("Add User Details")
        self.label_add_user.setAlignment(Qt.AlignCenter)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")
        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Phone Number")

        self.btn_add_user = QPushButton("Add User")

        right_layout.addWidget(self.label_add_user)
        right_layout.addWidget(self.input_username)
        right_layout.addWidget(self.input_email)
        right_layout.addWidget(self.input_phone)
        right_layout.addWidget(self.btn_add_user)

        # Dodanie sekcji do głównego układu
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.center_panel, 1)  # Zajmuje większość miejsca
        main_layout.addWidget(self.right_panel)

        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
