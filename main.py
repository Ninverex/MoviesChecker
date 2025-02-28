import sys
from PySide6.QtWidgets import QApplication
from LoginScreen import LoginScreen
from MainWindow import MainWindow

class AppManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_screen = LoginScreen()
        self.main_window = None

        # Po poprawnym logowaniu otwiera okno główne
        self.login_screen.login_success.connect(self.show_main_window)

        self.login_screen.show()
        sys.exit(self.app.exec())

    def show_main_window(self):
        self.login_screen.close()  # Zamknięcie ekranu logowania
        self.main_window = MainWindow()  # Uruchomienie aplikacji głównej
        self.main_window.show()

if __name__ == "__main__":
    AppManager()
