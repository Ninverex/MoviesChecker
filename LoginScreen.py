from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QSpacerItem, QSizePolicy
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Signal, Qt
from RegisterDialog import RegisterDialog
from database import login_user

class LoginScreen(QWidget):
    login_success = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet("""
            background-color: #121212;
            color: white;
            border-radius: 15px;
        """)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tytuł
        self.label_title = QLabel("Welcome Back!")
        self.label_title.setFont(QFont("Arial", 20, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_title)

        # Pole loginu
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Enter your login")
        self.input_login.setStyleSheet(self.input_style())
        self.layout.addWidget(self.input_login)

        # Pole hasła
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Enter your password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(self.input_style())
        self.layout.addWidget(self.input_password)

        # Przycisk logowania
        self.login_button = QPushButton("Log In")
        self.login_button.setIcon(QIcon("icons/login.png"))
        self.login_button.setStyleSheet(self.button_style())
        self.login_button.clicked.connect(self.attempt_login)
        self.layout.addWidget(self.login_button)

        # Układ poziomy dla przycisku "Create an Account"
        self.register_layout = QHBoxLayout()
        self.register_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Przycisk rejestracji
        self.register_button = QPushButton("Create an Account")
        self.register_button.setStyleSheet(self.register_button_style())
        self.register_button.clicked.connect(self.open_register_dialog)

        self.register_layout.addWidget(self.register_button)
        self.layout.addLayout(self.register_layout)

        self.setLayout(self.layout)

    def open_register_dialog(self):
        dialog = RegisterDialog(self)
        dialog.exec()

    def attempt_login(self):
        login = self.input_login.text()
        password = self.input_password.text()

        if login_user(login, password):
            QMessageBox.information(self, "Success", "Login successful!")
            self.login_success.emit()
        else:
            QMessageBox.warning(self, "Error", "Invalid login or password!")

    def input_style(self):
        return """
            background: rgba(255, 255, 255, 0.2);
            border: none;
            padding: 10px;
            border-radius: 10px;
            color: white;
            font-size: 14px;
        """

    def button_style(self):
        return """
            QPushButton {
                background-color: #1E88E5;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """

    def register_button_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: #BB86FC;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """
