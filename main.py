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

        # Ustawienie user_id w MainWindow po zalogowaniu
        self.main_window.logged_in_user_id = self.login_screen.logged_in_user_id

        self.main_window.logout_success.connect(self.show_login_screen)  # Połączenie sygnału logout_success
        self.main_window.show()

    def show_login_screen(self):
        self.main_window.close()  # Zamknięcie głównego okna
        self.login_screen = LoginScreen()  # Ponowne otwarcie ekranu logowania
        self.login_screen.login_success.connect(self.show_main_window)  # Ponowne połączenie sygnału login_success
        self.login_screen.show()

if __name__ == "__main__":
    AppManager()