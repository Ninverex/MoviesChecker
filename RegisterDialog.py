from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt
from database import register_user


class RegisterDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setGeometry(150, 150, 400, 500)
        self.setStyleSheet("""
            background-color: #121212;
            color: white;
            border-radius: 15px;
        """)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tytuł
        self.label_title = QLabel("Create an Account")
        self.label_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_title)

        # Pole email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Enter your email")
        self.input_email.setStyleSheet(self.input_style())
        self.layout.addWidget(self.input_email)

        # Pole loginu
        self.input_login = QLineEdit()
        self.input_login.setPlaceholderText("Choose a username")
        self.input_login.setStyleSheet(self.input_style())
        self.layout.addWidget(self.input_login)

        # Pole hasła
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Create a password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet(self.input_style())
        self.layout.addWidget(self.input_password)

        # Przycisk rejestracji
        self.register_button = QPushButton("Sign Up")
        self.register_button.setIcon(QIcon("icons/register.png"))
        self.register_button.setStyleSheet(self.button_style())
        self.register_button.clicked.connect(self.complete_registration)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def complete_registration(self):
        email = self.input_email.text()
        login = self.input_login.text()
        password = self.input_password.text()

        if not email or not login or not password:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        if register_user(email, login, password):
            QMessageBox.information(self, "Success", "Registration complete!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Username or email already exists!")

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
                background-color: #03DAC6;
                color: black;
                font-size: 16px;
                padding: 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #018786;
            }
        """
